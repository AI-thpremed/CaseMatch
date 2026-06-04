
from tqdm import tqdm
import os
import sys
import json
import datetime
from pathlib import Path
from multiprocessing import Queue
import torch
import torch.nn as nn
from torchvision import transforms
from PIL import Image
import numpy as np
from sklearn.manifold import TSNE
import matplotlib.pyplot as plt
import pandas as pd
from models.resnet import resnet50


def safe_write(msg):
    try:
        if getattr(sys, 'frozen', False) and (sys.stdout is None or sys.stderr is None):
            return
        from tqdm import tqdm
        tqdm.write(msg)
    except (AttributeError, ImportError, TypeError):
        pass


def update_worker(project_path: str, log_q: Queue):
    """
    Incremental Update of Retrieval Index
    1. Scan directory and extract features only for newly added images
    2. Detect deleted images and remove them from the index
    3. Overwrite the original file directly
    """
    # --- 1. Initialize path and logs ---


    project_path = Path(project_path)
    timestamp = datetime.datetime.now().strftime('%Y%m%d_%H%M%S')
    log_file_path = project_path / f'update_{timestamp}.log'
    log_file = open(log_file_path, 'a', encoding='utf-8')

    # 然后在 log 函数中使用：
    def log(msg, level="INFO"):
        nonlocal log_file
        if msg is None:
            log_q.put(None)
            if log_file:
                log_file.close()
            return
        if level == "INFO":
            log_q.put(msg)
        if log_file:
            log_file.write(msg + '\n')
            log_file.flush()

        safe_write(msg)  # 替代原来的 tqdm.write(msg)

    try:
        log("Starting incremental update...")

        config_file = project_path / "project_config.json"
        if not config_file.exists():
            raise FileNotFoundError(f"Config file not found: {config_file}")

        with open(config_file, 'r', encoding='utf-8') as f:
            cfg = json.load(f)

        image_dir = cfg.get('image_path')
        project_name = cfg.get('project_name', 'unknown')
        model_path = None
        if config_file.exists():
            with open(config_file, 'r', encoding='utf-8') as f:
                cfg = json.load(f)
                model_cfg = cfg.get('model', {})
                model_path = model_cfg.get('model_path')
                batch_size = cfg.get('batch_size', 16)
                input_size = cfg.get('input_size', 224)
                resize_before_crop = cfg.get('resize_before_crop', 256)

        res_dir = project_path

        if not image_dir or not os.path.exists(image_dir):
            raise ValueError(f"The image path is invalid: {image_dir}")

        # ==================== Scan all images in the current directory ====================
        valid_exts = ('.png', '.jpg', '.jpeg', '.bmp', '.tiff', '.gif', '.webp', '.tif')
        current_image_files = []
        for root, dirs, files in os.walk(image_dir):
            for file in files:
                if file.lower().endswith(valid_exts):
                    full_path = os.path.abspath(os.path.join(root, file))
                    current_image_files.append(full_path)

        current_image_files.sort()
        current_set = set(current_image_files)
        total_current = len(current_image_files)

        log(f"Scanned {total_current} images in current directory")

        # ==================== Load Model ====================
        device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        log(f"Using Device: {device}")

        transform = transforms.Compose([
            transforms.Resize(int(resize_before_crop)),
            transforms.CenterCrop(int(input_size)),
            transforms.ToTensor(),
            transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225])
        ])

        log("Load ResNet50 Model...")
        model = resnet50(pretrained=False)
        model.fc = nn.Identity()

        if os.path.exists(model_path):
            state_dict = torch.load(model_path, map_location="cpu", weights_only=False)
            model.load_state_dict(state_dict, strict=False)
            log(f"Loaded model weights: {model_path}")
        else:
            log(f"Warning: Model file not found, using random initialization: {model_path}", "WARNING")

        model = model.to(device)
        model.eval()

        # ==================== Two Strategy Definitions ====================
        strategies = [
            {
                "name": "avgpool_2048",
                "layer": "avgpool",
                "pooling": "gap",
                "desc": "Standard Global Features (2048-D)"
            },
            {
                "name": "layer4_gem_2048",
                "layer": "layer4",
                "pooling": "gem",
                "desc": "Deep Local Features + Saliency Pooling (2048-D)"
            }
        ]

        manifest = {
            "project_name": project_name,
            "timestamp": timestamp,
            "total_images": total_current,
            "strategies": {}
        }

        final_all_paths = None

        # ==================== Incremental update by strategy ====================
        for strategy in strategies:
            s_name = strategy["name"]
            s_desc = strategy["desc"]
            s_layer = strategy["layer"]
            s_pooling = strategy["pooling"]

            log(f"\n========== strategy: {s_desc} ==========")
            strategy_dir = res_dir / s_name

            # --- Load existing index ---
            existing_paths = []
            existing_feats = None
            features_file = strategy_dir / 'features.npy'
            list_file = strategy_dir / 'image_list.txt'

            if features_file.exists() and list_file.exists():
                try:
                    existing_feats = np.load(features_file)
                    with open(list_file, 'r', encoding='utf-8') as f:
                        existing_paths = [line.strip() for line in f if line.strip()]
                    log(f"[{s_name}] Existing index: {len(existing_paths)} images, feature dim: {existing_feats.shape}")
                except Exception as e:
                    log(f"[{s_name}] Failed to load existing index: {e}, will perform full rebuild", "WARNING")
                    existing_paths = []
                    existing_feats = None
            else:
                log(f"[{s_name}] Existing index not found, will perform full rebuild", "WARNING")

            existing_set = set(existing_paths)

            # --- Compute differences ---
            added_paths = [p for p in current_image_files if p not in existing_set]
            removed_paths = [p for p in existing_paths if p not in current_set]
            kept_paths = [p for p in existing_paths if p in current_set]

            log(f"[{s_name}] Added: {len(added_paths)} images, Removed: {len(removed_paths)} images, Kept: {len(kept_paths)} images")

            # --- Reuse existing features if no changes ---
            if len(added_paths) == 0 and len(removed_paths) == 0 and existing_feats is not None:
                log(f"[{s_name}] No changes, reusing existing features")
                all_paths = existing_paths
                feats = existing_feats
            else:
                # ========== BATCHED feature extraction for added images ==========
                added_feats_list = []   # stores [B, 2048] numpy arrays
                valid_added_paths = []   # paths that were successfully extracted

                if added_paths:
                    handle = None
                    hook_features = {}

                    if s_layer == "layer4":
                        def make_hook(container):
                            def hook_fn(module, input, output):
                                container['feat'] = output.detach()
                            return hook_fn

                        handle = model.layer4.register_forward_hook(make_hook(hook_features))

                    with torch.no_grad():
                        for i in range(0, len(added_paths), batch_size):
                            batch_paths = added_paths[i:i + batch_size]
                            batch_tensors = []
                            batch_valid_paths = []

                            for img_path in batch_paths:
                                try:
                                    img = Image.open(img_path).convert('RGB')
                                    batch_tensors.append(transform(img))
                                    batch_valid_paths.append(img_path)
                                except Exception as e:
                                    log(f"[{s_name}] Skipped {img_path}: {str(e)}", "WARNING")
                                    continue

                            if not batch_tensors:
                                continue

                            batch = torch.stack(batch_tensors).to(device)

                            if s_layer == "layer4":
                                hook_features.clear()

                            output = model(batch)

                            if s_layer == "avgpool":
                                # model.fc=Identity, so output is already [B, 2048]
                                batch_feat = output.cpu().numpy()
                            elif s_layer == "layer4":
                                feat_4d = hook_features['feat']  # [B, 2048, H, W]
                                p = 3.0
                                batch_feat = torch.mean(feat_4d.clamp(min=1e-6) ** p, dim=[2, 3]) ** (1.0 / p)
                                batch_feat = batch_feat.cpu().numpy()
                            else:
                                raise ValueError(f"dont support such layer: {s_layer}")

                            added_feats_list.append(batch_feat)
                            valid_added_paths.extend(batch_valid_paths)

                            total_processed = len(valid_added_paths)
                            if total_processed % 50 == 0 or (i + batch_size) >= len(added_paths):
                                log(f"[{s_name}] Processed {total_processed}/{len(added_paths)} added images")

                    if handle:
                        handle.remove()

                # --- Merge: keep existing features (not deleted) + new features ---
                added_feats = np.vstack(added_feats_list) if added_feats_list else None

                if existing_feats is not None and len(kept_paths) > 0:
                    path_to_idx = {p: i for i, p in enumerate(existing_paths)}
                    kept_indices = [path_to_idx[p] for p in kept_paths]
                    kept_feats = existing_feats[kept_indices]

                    if added_feats is not None:
                        feats = np.vstack([kept_feats, added_feats])
                        all_paths = kept_paths + valid_added_paths
                    else:
                        feats = kept_feats
                        all_paths = kept_paths
                else:
                    if added_feats is not None:
                        feats = added_feats
                        all_paths = valid_added_paths
                    else:
                        log(f"[{s_name}] No features successfully extracted, skipping", "ERROR")
                        continue

            # --- L2 Norm ---
            norms = np.linalg.norm(feats, axis=1, keepdims=True)
            feats = feats / (norms + 1e-8)

            # --- Save (overwrite original file)----
            strategy_dir.mkdir(exist_ok=True)
            np.save(strategy_dir / 'features.npy', feats)
            with open(strategy_dir / 'image_list.txt', 'w', encoding='utf-8') as f:
                for p in all_paths:
                    f.write(p + '\n')

            info = {
                "name": s_name,
                "desc": s_desc,
                "layer": s_layer,
                "pooling": s_pooling,
                "feature_dim": int(feats.shape[1]),
                "num_images": len(all_paths),
                "features_file": str(strategy_dir / 'features.npy'),
                "list_file": str(strategy_dir / 'image_list.txt')
            }
            with open(strategy_dir / 'strategy_info.json', 'w', encoding='utf-8') as f:
                json.dump(info, f, indent=2, ensure_ascii=False)

            log(f"[{s_name}] Completed: features {feats.shape}, saved to {strategy_dir}")
            manifest["strategies"][s_name] = info
            final_all_paths = all_paths

            # --- Regenerate t-SNE  ---
            if len(feats) > 1:
                try:
                    log(f"[{s_name}] Start t-SNE dimensionality reduction ...")
                    perplexity = min(30, len(feats) - 1)
                    tsne = TSNE(n_components=2, random_state=42, perplexity=perplexity, init='pca')
                    feats_2d = tsne.fit_transform(feats)

                    plt.figure(figsize=(10, 8))
                    plt.scatter(feats_2d[:, 0], feats_2d[:, 1],
                                alpha=0.6, s=10, c='steelblue', edgecolors='none')
                    plt.title(f'{s_desc}\nt-SNE (n={len(feats)})')
                    plt.xlabel('t-SNE 1')
                    plt.ylabel('t-SNE 2')
                    plt.grid(True, alpha=0.3)
                    plt.tight_layout()

                    tsne_path = strategy_dir / 'tsne.png'
                    plt.savefig(tsne_path, dpi=300, bbox_inches='tight')
                    plt.close()
                    log(f"[{s_name}] t-SNE Saved: {tsne_path}")
                except Exception as e:
                    log(f"[{s_name}] t-SNE Failed: {str(e)}", "WARNING")

        # ==================== Save the image list and configuration ====================
        cfg['timestamp'] = timestamp
        cfg['vectorized_count'] = total_current

        manifest_path = res_dir / 'manifest.json'
        with open(manifest_path, 'w', encoding='utf-8') as f:
            json.dump(manifest, f, indent=2, ensure_ascii=False)
        log(f"Index manifest saved: {manifest_path}")

        cfg_save_path = res_dir / 'project_config.json'
        with open(cfg_save_path, 'w', encoding='utf-8') as f:
            json.dump(cfg, f, indent=4, ensure_ascii=False)

        # --- Save CSV ---
        if final_all_paths:
            csv_path = res_dir / "query_dataset.csv"
            try:
                df = pd.DataFrame({'image': final_all_paths})
                df.to_csv(csv_path, index=False, encoding='utf-8')
                log(f"Retrieval results CSV saved: {csv_path}")
            except Exception as e:
                log(f"Failed to save CSV: {e}", "WARNING")

        log(f"Retrieval results CSV saved: {res_dir}")
        log("Incremental update completed successfully.")

    except Exception as e:
        log(f"Update error: {e}", "ERROR")
        raise
    finally:
        if log_file:
            log_file.close()
        log(None)
