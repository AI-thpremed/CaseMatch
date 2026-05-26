# -*- coding: utf-8 -*-
import os
import sys
import json
import datetime
from pathlib import Path
from typing import Optional, List, Tuple
from multiprocessing import Process, Queue

from PySide6.QtWidgets import (
    QWidget, QFileDialog, QMessageBox, QLabel, QVBoxLayout,
    QHBoxLayout, QPushButton, QLineEdit, QComboBox, QTextEdit,
    QGroupBox
)
from PySide6.QtCore import Qt, QObject, Signal, Slot, QTimer
from PySide6.QtGui import QPixmap, QImage
from PIL import Image
import numpy as np

from ui_retrieval import Ui_RetrievalWindow
from retrieval_worker import retrieval_process


class RetrievalManager(QObject):
    log = Signal(str)
    finished = Signal(bool, list)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.proc: Optional[Process] = None
        self.log_q: Optional[Queue] = None
        self.result_q: Optional[Queue] = None
        self.timer = QTimer(self)
        self.timer.timeout.connect(self._read_output)

    def start_retrieval(self, cfg: dict):
        if self.proc is not None and self.proc.is_alive():
            self.log.emit("[WARNING] Another retrieval is already running!")
            return

        self.log_q = Queue()
        self.result_q = Queue()

        self.proc = Process(
            target=retrieval_process,
            args=(cfg, self.log_q, self.result_q),
            daemon=True
        )
        self.proc.start()
        self.timer.start(200)

    def _read_output(self):
        if self.log_q is None:
            return


        while not self.log_q.empty():
            try:
                msg = self.log_q.get_nowait()

                if msg is None:
                    self.timer.stop()


                    if self.proc is not None and self.proc.is_alive():
                        self.proc.join(timeout=2)


                    results = []
                    try:
                        if not self.result_q.empty():
                            results = self.result_q.get_nowait()
                    except Exception:
                        pass

                    success = len(results) > 0
                    self.finished.emit(success, results)
                    break
                elif isinstance(msg, str):
                    self.log.emit(msg)

            except Exception as e:
                self.log.emit(f"[ERROR] Log read error: {e}")
                break

    def stop(self):
        if self.proc is not None and self.proc.is_alive():
            self.proc.terminate()
            self.proc.join()
            self.log.emit("[WARNING] Retrieval terminated by user")


class RetrievalWindow(QWidget, Ui_RetrievalWindow):

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setupUi(self)


        self.current_project_path: Optional[str] = None
        self.current_query_path: Optional[str] = None
        self.last_results: Optional[List[Tuple[str, float, Optional[str]]]] = None


        self.retrieval_mgr = RetrievalManager(self)
        self.retrieval_mgr.log.connect(self._on_log_received)
        self.retrieval_mgr.finished.connect(self._on_retrieval_finished)


        self.result_labels = [
            (self.label_result_1, self.label_score_1),
            (self.label_result_2, self.label_score_2),
            (self.label_result_3, self.label_score_3),
            (self.label_result_4, self.label_score_4),
            (self.label_result_5, self.label_score_5),
        ]

        self._setup_connections()
        self._clear_results()
        self._log("Ready for image retrieval...")

    def _setup_connections(self):
        self.btn_load.clicked.connect(self._on_load_project)
        self.btn_open_image.clicked.connect(self._on_select_query)
        self.btn_start_retrieval.clicked.connect(self._on_start_retrieval)

    def _clear_results(self):
        for img_label, score_label in self.result_labels:
            img_label.setText("Waiting...")
            img_label.setStyleSheet("")
            score_label.setText("Similarity: --")
        self.last_results = None

    def _log(self, message: str):
        if message is None:
            return
        self.text_log.append(message)
        self.text_log.ensureCursorVisible()

    @Slot(str)
    def _on_log_received(self, msg: str):
        self._log(msg)

    @Slot(bool, list)
    def _on_retrieval_finished(self, success: bool, results: list):
        self.btn_start_retrieval.setEnabled(True)
        self.btn_start_retrieval.setText("Start Retrieval")

        if not success:
            QMessageBox.warning(self, "Retrieval Failed", "No results found or process error.")
            return

        self.last_results = results
        self._display_results(results)
        self._log(f"[DONE] Retrieved {len(results)} results")

    def _on_load_project(self):
        """Load project folder (adapted for dual-strategy indexing)"""
        folder = QFileDialog.getExistingDirectory(
            self, "Select Project Folder", "",
            QFileDialog.ShowDirsOnly | QFileDialog.DontResolveSymlinks
        )
        if not folder:
            return

        self.current_project_path = folder
        self.line_project_path.setText(folder)
        self._log(f"Project loaded: {folder}")

        project_path = Path(folder)
        config_file = project_path / "project_config.json"

        if not config_file.exists():
            QMessageBox.warning(self, "Invalid Project", "No project_config.json found.")
            return

        with open(config_file, 'r', encoding='utf-8') as f:
            cfg = json.load(f)

        # Get results directory
        results_dir_str = cfg.get('results')
        if not results_dir_str:
            QMessageBox.warning(self, "Invalid Config", "Missing 'results' path in config.")
            return

        results_dir = Path(results_dir_str)

        # Read manifest to check both strategy indexes
        manifest_file = results_dir / 'manifest.json'
        if not manifest_file.exists():
            self._log("Warning: No manifest found. Please build index first.", "WARNING")
            QMessageBox.warning(self, "No Index",
                                "Project has no built index. Please build or rebuild the index first.")
            return

        with open(manifest_file, 'r', encoding='utf-8') as f:
            manifest = json.load(f)

        total_images = manifest.get('total_images', 0)
        all_ready = True

        # Check two fixed strategies
        for s_name in ('avgpool_2048', 'layer4_gem_2048'):
            s_info = manifest.get('strategies', {}).get(s_name)
            if not s_info:
                self._log(f"  [{s_name}] Index missing: no record in manifest", "WARNING")
                all_ready = False
                continue

            feat_file = Path(s_info.get('features_file', ''))
            list_file = Path(s_info.get('list_file', ''))

            if feat_file.exists() and list_file.exists():
                count = s_info.get('num_images', 0)
                dim = s_info.get('feature_dim', 0)
                self._log(f"  [{s_name}] Index ready: {count} images, {dim} dims")
            else:
                self._log(f"  [{s_name}] Index file missing", "WARNING")
                all_ready = False

        if not all_ready:
            self._log("Warning: Some indexes are missing, please rebuild project index", "WARNING")
            QMessageBox.warning(
                self, "Incomplete Index",
                "Some feature indexes are missing or corrupted.\n"
                "Please rebuild the project index to generate the complete dual-strategy retrieval space."
            )
        else:
            self._log(f"Dual-strategy indexes all ready, total {total_images} images")

    def _on_select_query(self):
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Select Query Image", "",
            "Images (*.png *.jpg *.jpeg *.bmp *.tiff *.webp);;All Files (*)"
        )
        if not file_path:
            return

        self.current_query_path = file_path
        self.line_image_path.setText(file_path)
        self._display_query_image(file_path)
        self._log(f"Query image selected: {file_path}")

    def _display_query_image(self, path: str):
        pixmap = self._load_image_pixmap(path, size=(300, 300))
        if pixmap:
            self.label_query_image.setPixmap(pixmap)
            self.label_query_image.setScaledContents(True)
        else:
            self.label_query_image.setText("Failed to load image")

    def _load_image_pixmap(self, path: str, size: Tuple[int, int]) -> Optional[QPixmap]:
        try:

            img = Image.open(path)


            if img.mode not in ('RGB', 'L'):
                img = img.convert('RGB')
            elif img.mode == 'L':
                img = img.convert('RGB')

            img.thumbnail(size, Image.Resampling.LANCZOS)
            data = img.tobytes("raw", "RGB")
            qim = QImage(data, img.width, img.height, img.width * 3, QImage.Format_RGB888)
            pixmap = QPixmap.fromImage(qim)
            return pixmap

        except Exception as e:

            try:
                pixmap = QPixmap(path)
                if not pixmap.isNull():
                    return pixmap.scaled(size[0], size[1], Qt.KeepAspectRatio, Qt.SmoothTransformation)
            except Exception:
                pass

            self._log(f"Error loading image {path}: {e}")
            return None

    #
    # def _load_image_pixmap(self, path: str, size: Tuple[int, int]) -> Optional[QPixmap]:

    #     try:
    #         img = Image.open(path).convert('RGB')
    #         img.thumbnail(size, Image.Resampling.LANCZOS)
    #
    #         data = img.tobytes("raw", "RGB")
    #         qim = QImage(data, img.width, img.height, img.width * 3, QImage.Format_RGB888)
    #         pixmap = QPixmap.fromImage(qim)
    #         return pixmap
    #     except Exception as e:
    #         self._log(f"Error loading image {path}: {e}")
    #         return None

    def _display_results(self, results: List[Tuple[str, float, Optional[str]]]):
        self._clear_results()
        actual_k = min(len(results), 5)
        self.groupRetrieved.setTitle(f"Top {actual_k} Similar Images")

        for i, result in enumerate(results[:5]):
            if i >= len(self.result_labels):
                break

            img_label, score_label = self.result_labels[i]


            if len(result) >= 3:
                img_path, score, cam_dir = result[0], result[1], result[2]
            elif len(result) == 2:
                img_path, score = result
                cam_dir = None
            else:
                continue

            pixmap = self._load_image_pixmap(img_path, size=(200, 200))
            if pixmap:
                img_label.setPixmap(pixmap)
                img_label.setScaledContents(True)
            else:
                img_label.setText("Error")

            score_str = f"{score * 100:.1f}%" if isinstance(score, (int, float)) and score <= 1 else f"{score:.2f}"
            score_label.setText(f"Similarity: {score_str}")
            score_label.setStyleSheet("font-weight: bold; color: #0066cc;")

            tooltip = f"Path: {img_path}\nScore: {score}"
            if cam_dir:
                tooltip += f"\nCAM: {cam_dir}"
            img_label.setToolTip(tooltip)

    def _on_start_retrieval(self):
        if not self.current_project_path:
            QMessageBox.warning(self, "Missing Project", "Please load a project first.")
            return
        if not self.current_query_path:
            QMessageBox.warning(self, "Missing Query", "Please select a query image.")
            return

        top_k = int(self.combo_topk.currentText())
        method = self.combo_method.currentText()

        cfg = {
            "project_path": self.current_project_path,
            "query_image_path": self.current_query_path,
            "top_k": top_k,
            "strategy_name": method,
        }

        self.btn_start_retrieval.setEnabled(False)
        self.btn_start_retrieval.setText("Retrieving...")
        self.text_log.clear()
        self._log(f"[START] Launching retrieval process...")

        self.retrieval_mgr.start_retrieval(cfg)

    def closeEvent(self, event):
        if self.retrieval_mgr.proc and self.retrieval_mgr.proc.is_alive():
            self.retrieval_mgr.stop()
        event.accept()


def main():
    if sys.platform == 'win32':
        import multiprocessing
        multiprocessing.freeze_support()

    app = QApplication(sys.argv)
    app.setStyle('Fusion')
    window = RetrievalWindow()
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()