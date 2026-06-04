import os, sys, json, datetime, traceback
from pathlib import Path
from typing import List, Tuple, Optional
from queue import Queue
from multiprocessing import Queue as MPQueue

import torch
import torch.nn as nn
import numpy as np
import cv2
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from torchvision import transforms
from PIL import Image
import time

from models.resnet import resnet50
import pandas as pd
import shutil
# ==================== GradCAM ====================
class GradCAM:
    def __init__(self, model, target_layer):
        self.model = model
        self.target_layer = target_layer
        self.gradients = None
        self.activations = None
        self.target_layer.register_forward_hook(self.save_activation)
        self.target_layer.register_full_backward_hook(self.save_gradient)

    def save_activation(self, module, input, output):
        self.activations = output.detach()

    def save_gradient(self, module, grad_input, grad_output):
        self.gradients = grad_output[0].detach()

    def generate_cam(self, input_tensor, target_category=None):
        model_output = self.model(input_tensor)
        if target_category is None:
            loss = model_output.norm()
        else:
            loss = model_output[0, target_category]
        self.model.zero_grad()
        loss.backward(retain_graph=True)
        gradients = self.gradients[0].cpu().numpy()
        activations = self.activations[0].cpu().numpy()
        weights = np.mean(gradients, axis=(1, 2))
        cam = np.zeros(activations.shape[1:], dtype=np.float32)
        for i, w in enumerate(weights):
            cam += w * activations[i]
        cam = np.maximum(cam, 0)
        cam = cam - cam.min()
        if cam.max() != 0:
            cam = cam / cam.max()
        return cam, model_output.detach()





def visualize_cam_on_image(img_pil, cam, alpha=0.5):

    if img_pil.mode != 'RGB':
        img_pil = img_pil.convert('RGB')

    img_array = np.array(img_pil)
    h, w = img_array.shape[:2]
    cam_resized = cv2.resize(cam, (w, h))
    heatmap = cv2.applyColorMap(np.uint8(255 * cam_resized), cv2.COLORMAP_JET)
    heatmap = cv2.cvtColor(heatmap, cv2.COLOR_BGR2RGB)
    overlay = heatmap * alpha + img_array * (1 - alpha)
    return img_array, heatmap, overlay.astype(np.uint8)

def create_comparison_figure(query_img_path, query_cam, retrieved_info_list, save_path, log_callback=None):
    log = log_callback or (lambda m, l="INFO": None)
    n_imgs = len(retrieved_info_list) + 1
    fig, axes = plt.subplots(n_imgs, 3, figsize=(12, 4 * n_imgs))
    if n_imgs == 1:
        axes = axes.reshape(1, -1)

    query_img = Image.open(query_img_path)
    if query_img.mode != 'RGB':
        query_img = query_img.convert('RGB')

    _, _, query_overlay = visualize_cam_on_image(query_img, query_cam, alpha=0.5)
    axes[0, 0].imshow(query_img)
    axes[0, 0].set_title('Query (Original)', fontsize=10)
    axes[0, 0].axis('off')
    axes[0, 1].imshow(query_cam, cmap='jet')
    axes[0, 1].set_title('Query CAM', fontsize=10)
    axes[0, 1].axis('off')
    axes[0, 2].imshow(query_overlay)
    axes[0, 2].set_title('Query Overlay', fontsize=10)
    axes[0, 2].axis('off')

    for idx, info in enumerate(retrieved_info_list):
        img_path = info['path']
        cam = info['cam']
        score = info['score']
        try:
            img = Image.open(img_path)
            if img.mode != 'RGB':
                img = img.convert('RGB')

            _, _, overlay = visualize_cam_on_image(img, cam, alpha=0.5)
            row = idx + 1
            axes[row, 0].imshow(img)
            axes[row, 0].set_title(f"Top{idx+1}: {os.path.basename(img_path)}\nCosine: {score:.4f}", fontsize=9)
            axes[row, 0].axis('off')
            axes[row, 1].imshow(cam, cmap='jet')
            axes[row, 1].set_title('CAM', fontsize=9)
            axes[row, 1].axis('off')
            axes[row, 2].imshow(overlay)
            axes[row, 2].set_title('Overlay', fontsize=9)
            axes[row, 2].axis('off')
        except Exception as e:
            log(f"Failed to visualize result {idx+1}: {e}", "WARNING")

    plt.tight_layout()
    plt.savefig(save_path, dpi=150, bbox_inches='tight')
    plt.close()
    log(f"Comparison figure saved: {save_path}", "INFO")


def get_app_path():
    """获取应用程序的根目录（开发环境返回项目目录，打包环境返回exe所在目录）"""
    if getattr(sys, 'frozen', False):
        # PyInstaller 打包后，exe 所在目录
        return Path(sys.executable).parent
    else:
        # 开发环境，返回当前文件所在目录的父目录（或项目根目录）
        return Path(__file__).parent


# ==================== Core Worker ====================
def retrieval_worker(
    project_path: str,
    query_image_path: str,
    top_k: int,
    strategy_name: str,
    log_q
) -> List[Tuple[str, float, Optional[str]]]:
    """
    Dual-strategy retrieval Worker.
    strategy_name: avgpool_2048 | layer4_gem_2048
    """

    assert strategy_name in ('avgpool_2048', 'layer4_gem_2048'), f"Invalid strategy: {strategy_name}"

    log_file = None
    def log(msg, level="INFO"):
        nonlocal log_file
        if msg is None:
            if log_q is not None:
                log_q.put(None)
            if log_file:
                log_file.close()
            return
        time_str = datetime.datetime.now().strftime('%H:%M:%S')
        line = f"[{time_str}] [{level}] {msg}" if level != "INFO" else f"[{time_str}] {msg}"
        if log_file:
            log_file.write(line + '\n')
            log_file.flush()
        if log_q is not None:
            log_q.put(line)

    try:

        app_path = get_app_path()
        root_results = app_path / 'results'

        root_results.mkdir(exist_ok=True)
        start_time = time.time()


        proj = Path(project_path)
        timestamp = datetime.datetime.now().strftime('%Y%m%d_%H%M%S')
        res_dir = root_results / f'retrieval_{timestamp}'
        res_dir.mkdir(exist_ok=True)


        query_src = Path(query_image_path)
        shutil.copy2(query_src, res_dir / f"input_image{query_src.suffix}")

        log_file_path = res_dir / f'retrieval_{timestamp}.log'
        log_file = open(log_file_path, 'a', encoding='utf-8')

        log("=" * 50)
        log(f"Source Project: {project_path}")
        log(f"Starting retrieval | Strategy: {strategy_name} | Top-K: {top_k}")
        log(f"Query image: {query_image_path}")

        # 1. Read manifest
        manifest_path = proj / 'manifest.json'
        if not manifest_path.exists():
            raise FileNotFoundError(f"manifest.json not found: {manifest_path}")

        with open(manifest_path, 'r', encoding='utf-8') as f:
            manifest = json.load(f)

        if strategy_name not in manifest.get('strategies', {}):
            raise ValueError(f"No strategy in manifest: {strategy_name}")

        st_info = manifest['strategies'][strategy_name]
        feat_file = st_info['features_file']
        list_file = st_info['list_file']

        if not os.path.exists(feat_file):
            raise FileNotFoundError(f"Feature file does not exist: {feat_file}")
        if not os.path.exists(list_file):
            raise FileNotFoundError(f"List file does not exist: {list_file}")

        db_features = np.load(feat_file).astype(np.float32)
        with open(list_file, 'r', encoding='utf-8') as f:
            db_paths = [line.strip() for line in f if line.strip()]

        if len(db_features) != len(db_paths):
            raise ValueError(f"Feature count ({len(db_features)}) does not match path count ({len(db_paths)})")

        log(f"Index loaded: {len(db_paths)} images, dimension {db_features.shape[1]}")

        # 2. Read model path
        config_file = proj / 'project_config.json'
        model_path = None
        if config_file.exists():
            with open(config_file, 'r', encoding='utf-8') as f:
                cfg = json.load(f)
                model_cfg = cfg.get('model', {})
                model_path = model_cfg.get('model_path')
                input_size=cfg.get('input_size',224)
                resize_before_crop=cfg.get('resize_before_crop',256)

        # 3. Load full model (keep fc for GradCAM)
        device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        log(f"Using device: {device}")

        transform = transforms.Compose([
            transforms.Resize(int(resize_before_crop)),
            transforms.CenterCrop(int(input_size)),
            transforms.ToTensor(),
            transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225])
        ])

        log("Loading model checkpoints...")
        model = resnet50(pretrained=False)
        if model_path and os.path.exists(model_path):
            state_dict = torch.load(model_path, map_location="cpu", weights_only=False)
            model.load_state_dict(state_dict, strict=False)
            log(f"Loading weights: {model_path}")
        else:
            log(f"WARNING: Model weights not found, using random initialization", "WARNING")

        model = model.to(device).eval()
        target_layer = model.layer4[2].conv3
        grad_cam = GradCAM(model, target_layer)

        # 4. Extract query features
        query_img_pil = Image.open(query_image_path).convert('RGB')
        query_tensor = transform(query_img_pil).unsqueeze(0).to(device)

        layer_name = st_info['layer']
        pooling = st_info['pooling']
        hook_feat = None

        if layer_name == 'avgpool':
            def hook_fn(m, inp, out):
                nonlocal hook_feat
                hook_feat = out.detach()
            handle = model.avgpool.register_forward_hook(hook_fn)
            with torch.no_grad():
                _ = model(query_tensor)
            handle.remove()
            feat = hook_feat.flatten(1)
        elif layer_name == 'layer4':
            def hook_fn(m, inp, out):
                nonlocal hook_feat
                hook_feat = out.detach()
            handle = model.layer4.register_forward_hook(hook_fn)
            with torch.no_grad():
                _ = model(query_tensor)
            handle.remove()
            feat_4d = hook_feat
            if pooling == 'gem':
                p = 3.0
                feat = torch.mean(feat_4d.clamp(min=1e-6) ** p, dim=[2, 3]) ** (1.0 / p)
            else:
                feat = feat_4d.mean(dim=[2, 3])
        else:
            raise ValueError(f"Unsupported layer: {layer_name}")

        query_feat = feat.cpu().numpy()
        query_feat = query_feat / (np.linalg.norm(query_feat, axis=1, keepdims=True) + 1e-8)
        query_feat = query_feat[0]

        # 5. Query image GradCAM
        with torch.no_grad():
            logits = model(query_tensor)
            pred_class = int(logits.argmax(dim=1).item())
        query_cam, _ = grad_cam.generate_cam(query_tensor, target_category=pred_class)
        log(f"Query image predicted class index: {pred_class}")

        # 6. Retrieval ranking
        similarities = np.dot(db_features, query_feat)
        top_indices = np.argsort(similarities)[::-1][:top_k]
        log(f"Retrieval complete, returning Top-{top_k}")

        # 7. Result processing + GradCAM
        results_dir = res_dir / 'gradcam'
        results_dir.mkdir(exist_ok=True)

        _, query_heatmap, query_overlay = visualize_cam_on_image(query_img_pil, query_cam)
        cv2.imwrite(str(results_dir / "query_heatmap.jpg"),
                    cv2.cvtColor(query_heatmap, cv2.COLOR_RGB2BGR))
        cv2.imwrite(str(results_dir / "query_overlay.jpg"),
                    cv2.cvtColor(query_overlay, cv2.COLOR_RGB2BGR))

        retrieved_info = []
        output_results = []

        for rank, idx in enumerate(top_indices, start=1):
            score = float(similarities[idx])
            img_path = db_paths[idx]

            if not os.path.exists(img_path):
                log(f"Top{rank}: Image does not exist {img_path}", "WARNING")
                output_results.append((img_path, score, None))
                continue

            log(f"Top{rank}: {img_path} | Similarity: {score:.4f}")

            try:
                img_pil = Image.open(img_path)
                if img_pil.mode != 'RGB':
                    img_pil = img_pil.convert('RGB')
                img_tensor = transform(img_pil).unsqueeze(0).to(device)


                with torch.no_grad():
                    logits = model(img_tensor)
                    pred_class = int(logits.argmax(dim=1).item())
                cam, _ = grad_cam.generate_cam(img_tensor, target_category=pred_class)

                original, heatmap, overlay = visualize_cam_on_image(img_pil, cam)

                cam_subdir = results_dir / f"top{rank}_{Path(img_path).stem}"
                cam_subdir.mkdir(exist_ok=True)
                cv2.imwrite(str(cam_subdir / "original.jpg"),
                            cv2.cvtColor(original, cv2.COLOR_RGB2BGR))
                cv2.imwrite(str(cam_subdir / "heatmap.jpg"),
                            cv2.cvtColor(heatmap, cv2.COLOR_RGB2BGR))
                cv2.imwrite(str(cam_subdir / "overlay.jpg"),
                            cv2.cvtColor(overlay, cv2.COLOR_RGB2BGR))

                retrieved_info.append({'path': img_path, 'cam': cam, 'score': score})
                output_results.append((img_path, score, str(cam_subdir)))

            except Exception as e:
                log(f"Top{rank} GradCAM failed: {e}", "WARNING")
                output_results.append((img_path, score, None))

        # 8. Comparison overview
        if retrieved_info:
            comp_path = results_dir / "comparison_overview.png"
            create_comparison_figure(
                query_image_path, query_cam, retrieved_info,
                str(comp_path), log_callback=log
            )
        # ===== New: Save CSV results using pandas =====
        csv_path = res_dir / "retrieval_results.csv"
        try:
            df = pd.DataFrame({
                'id': range(1, len(output_results) + 1),
                'image': [item[0] for item in output_results],
                'similarity': [f"{item[1]:.6f}" for item in output_results]
            })
            df.to_csv(csv_path, index=False, encoding='utf-8')
            log(f"Retrieval results CSV saved: {csv_path}")
        except Exception as e:
            log(f"Failed to save CSV: {e}", "WARNING")
        # ===========================================


        log(f"Retrieval data saved in {res_dir}")
        elapsed = time.time() - start_time
        log(f"Total elapsed time: {elapsed:.2f} seconds ({elapsed/60:.2f} minutes)")
        log("Retrieval process completed")
        log("=" * 50)
        return output_results

    except Exception as e:
        err = f"Retrieval error: {str(e)}\n{traceback.format_exc()}"
        log(err, "ERROR")
        return []

    finally:

        log(None)


# ==================== entry ====================
def retrieval_process(cfg: dict, log_q: MPQueue, result_q: MPQueue):
    try:
        class LogAdapter:
            def __init__(self, mp_queue):
                self.q = mp_queue
            def put(self, msg):
                self.q.put(msg)
        adapter = LogAdapter(log_q)

        results = retrieval_worker(
            project_path=cfg['project_path'],
            query_image_path=cfg['query_image_path'],
            top_k=cfg.get('top_k', 5),
            strategy_name=cfg.get('strategy_name', 'avgpool_2048'),
            log_q=adapter
        )
        result_q.put(results)

    except Exception as e:
        err = f"[ERROR] Process crashed: {str(e)}\n{traceback.format_exc()}"
        log_q.put(err)
        log_q.put(None)
        result_q.put([])