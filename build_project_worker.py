import os, sys, json, datetime, torch
from pathlib import Path
from tqdm import tqdm
from torchvision import transforms
import torch.nn as nn
import torch.nn.functional as F
from PIL import Image
from sklearn.manifold import TSNE
import matplotlib.pyplot as plt
import numpy as np
from models.resnet import resnet50
import pandas as pd
import time
from config_manager import ConfigManager

class TqdmToLog:
    def __init__(self, log_func):
        self.log_func = log_func

    def write(self, buf):
        for line in buf.rstrip().splitlines():
            self.log_func(line.rstrip())

    def flush(self):
        pass

def get_app_path():
    """获取应用程序的根目录（开发环境返回项目目录，打包环境返回exe所在目录）"""
    if getattr(sys, 'frozen', False):
        # PyInstaller 打包后，exe 所在目录
        return Path(sys.executable).parent
    else:
        # 开发环境，返回当前文件所在目录的父目录（或项目根目录）
        return Path(__file__).parent


def safe_write(msg):
    """安全的控制台写入，在打包后的 GUI 应用中自动禁用"""
    try:
        if getattr(sys, 'frozen', False) and (sys.stdout is None or sys.stderr is None):
            return  # 打包后的 GUI 应用，没有控制台
        from tqdm import tqdm
        tqdm.write(msg)
    except (AttributeError, ImportError, TypeError):
        # 开发环境也可能没有 tqdm，静默处理
        pass




def build_project(cfg: dict, log_q):
    """
    Generate two standard feature libraries simultaneously:
      1. avgpool_2048  - Standard global features (2048-D)
      2. layer4_gem_2048 - Deep local features + saliency pooling (2048-D)
    No PCA, no sample limit, applicable to all datasets.
    """

    log_file = None

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

        safe_write(msg)

    start_time = time.time()

    config_manager = ConfigManager(config_path="config.json")
    config = config_manager.config
    batch_size = config["common"].get("batch_size", 16)
    input_size = config["common"].get("input_size", 224)
    resize_before_crop = config["common"].get("resize_before_crop", 256)



    cfg['batch_size'] = str(batch_size)
    cfg['input_size'] = str(input_size)
    cfg['resize_before_crop'] = str(resize_before_crop)

    app_path = get_app_path()
    root_cache = app_path / 'cache'
    root_results = app_path / 'results'

    root_cache.mkdir(exist_ok=True)
    root_results.mkdir(exist_ok=True)

    project_name = cfg['project_name']
    timestamp    = datetime.datetime.now().strftime('%Y%m%d_%H%M%S')
    res_dir      = root_results / f'project_{project_name}_{timestamp}'
    res_dir.mkdir(exist_ok=True)

    cfg['results'] = str(res_dir)

    log_file_path = res_dir / 'training.log'
    log_file = open(log_file_path, 'a', encoding='utf-8')

    try:
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

        image_dir  = cfg.get('image_path')
        model_path = cfg.get('model_path')

        if not image_dir or not os.path.exists(image_dir):
            raise ValueError(f"Invalid image path: {image_dir}")

        log(f"Starting feature extraction - image directory: {image_dir}")
        log(f"Main results directory: {res_dir}")

        device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        log(f"Using device: {device}")


        transform = transforms.Compose([
            transforms.Resize(resize_before_crop),
            transforms.CenterCrop(input_size),
            transforms.ToTensor(),
            transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225])
        ])

        # ==================== Load Model (fc=Identity) ====================
        log("Loading ResNet50 model...")
        model = resnet50(pretrained=False)
        model.fc = nn.Identity()

        if os.path.exists(model_path):
            state_dict = torch.load(model_path, map_location="cpu", weights_only=False)
            model.load_state_dict(state_dict, strict=False)
            log(f"Loading model weights: {model_path}")
        else:
            log(f"WARNING: Model file does not exist, using random initialization: {model_path}", "WARNING")

        model = model.to(device)
        model.eval()

        # ==================== Recursively Scan All Images (Single Scan) ====================
        valid_exts = ('.png', '.jpg', '.jpeg', '.bmp', '.tiff', '.gif', '.webp','.tif')
        image_files = []

        for root, dirs, files in os.walk(image_dir):
            for file in files:
                if file.lower().endswith(valid_exts):
                    full_path = os.path.abspath(os.path.join(root, file))
                    image_files.append(full_path)

        image_files.sort()
        total_images = len(image_files)

        if total_images == 0:
            raise ValueError(f"No valid images found in directory and subdirectories: {image_dir}")

        log(f"Recursive scan complete, found {total_images} images (including all subdirectories)")

        # ==================== Extract Per Strategy ====================
        manifest = {
            "project_name": project_name,
            "timestamp": timestamp,
            "total_images": total_images,
            "strategies": {}
        }

        for strategy in strategies:
            s_name = strategy["name"]
            s_desc = strategy["desc"]
            s_layer = strategy["layer"]
            s_pooling = strategy["pooling"]

            log(f"\n========== strategy: {s_desc} ==========")
            strategy_dir = res_dir / s_name
            strategy_dir.mkdir(exist_ok=True)

            # Register hook (layer4 only)
            handle = None
            hook_features = {}

            if s_layer == "layer4":
                def make_hook(container):
                    def hook_fn(module, input, output):
                        container['feat'] = output.detach()
                    return hook_fn
                handle = model.layer4.register_forward_hook(make_hook(hook_features))

            # Extract features
            all_feats = []
            all_paths = []

            with torch.no_grad():
                for i in range(0, total_images, batch_size):
                    batch_paths = image_files[i:i + batch_size]
                    batch_tensors = []
                    valid_paths = []

                    for img_path in batch_paths:
                        try:
                            img = Image.open(img_path).convert('RGB')
                            batch_tensors.append(transform(img))
                            valid_paths.append(img_path)
                        except Exception as e:
                            log(f"[{s_name}] Skipped {img_path}: {str(e)}", "WARNING")
                            continue

                    if len(batch_tensors) == 0:
                        continue

                    batch = torch.stack(batch_tensors).to(device)
                    _ = model(batch)

                    if s_layer == "avgpool":
                        feats_batch = model(batch)  # [B, 2048]
                        for b in range(feats_batch.size(0)):
                            all_feats.append(feats_batch[b].cpu().numpy().flatten())
                            all_paths.append(valid_paths[b])

                    elif s_layer == "layer4":
                        feat_4d = hook_features['feat']  # [B, C, H, W]
                        p = 3.0
                        for b in range(feat_4d.size(0)):
                            feat = torch.mean(feat_4d[b].clamp(min=1e-6) ** p, dim=[1, 2]) ** (1.0 / p)
                            all_feats.append(feat.cpu().numpy().flatten())
                            all_paths.append(valid_paths[b])

                    else:
                        raise ValueError(f"Unsupported layer: {s_layer}")

                    processed = min(i + len(valid_paths), total_images)
                    if processed % 50 == 0 or processed == total_images:
                        log(f"[{s_name}] Processed {processed}/{total_images} images")
            if handle:
                handle.remove()

            if len(all_feats) == 0:
                log(f"[{s_name}] No features successfully extracted, skipping", "ERROR")
                continue

            feats = np.array(all_feats, dtype=np.float32)
            log(f"[{s_name}] Original feature dimensions: {feats.shape}")

            # L2 normalization (prerequisite for cosine similarity retrieval)
            norms = np.linalg.norm(feats, axis=1, keepdims=True)
            feats = feats / (norms + 1e-8)

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

            log(f"[{s_name}] Complete: features {feats.shape}, saved to {strategy_dir}")
            manifest["strategies"][s_name] = info

            # t-SNE
            if len(feats) > 1:
                try:
                    log(f"[{s_name}] Starting t-SNE dimensionality reduction...")
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
                    log(f"[{s_name}] t-SNE saved: {tsne_path}")
                except Exception as e:
                    log(f"[{s_name}] t-SNE failed: {str(e)}", "WARNING")

        # ==================== Save Manifest ====================
        cfg['vectorized_count'] = total_images

        manifest_path = res_dir / 'manifest.json'
        with open(manifest_path, 'w', encoding='utf-8') as f:
            json.dump(manifest, f, indent=2, ensure_ascii=False)
        log(f"Index manifest saved: {manifest_path}")

        cfg_save_path = res_dir / 'project_config.json'
        with open(cfg_save_path, 'w', encoding='utf-8') as f:
            json.dump(cfg, f, indent=4, ensure_ascii=False)


        # ===== New: Save CSV results using pandas =====
        csv_path = res_dir / "query_dataset.csv"
        try:
            df = pd.DataFrame({
                'image': [item for item in all_paths]
            })
            df.to_csv(csv_path, index=False, encoding='utf-8')
            log(f"Retrieval results CSV saved: {csv_path}")
        except Exception as e:
            log(f"Failed to save CSV: {e}", "WARNING")
        # ===========================================
        log(f"Index data saved in {res_dir}")
        log("All two strategy feature extractions completed")

    except Exception as e:
        log(f"Feature extraction error: {e}", "ERROR")
        raise

    finally:
        elapsed = time.time() - start_time
        log(f"Total elapsed time: {elapsed:.2f} seconds ({elapsed/60:.2f} minutes)")
        if log_file:
            log_file.close()
        log(None)
