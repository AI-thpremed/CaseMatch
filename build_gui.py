# -*- coding: utf-8 -*-
import sys
import os
import json
import shutil
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Any, Tuple
from multiprocessing import Process, Queue
from PySide6.QtWidgets import (
    QApplication, QWidget, QMessageBox, QFileDialog
)
from PySide6.QtCore import QObject, QTimer, Signal
from build_project_worker import build_project
from ui_build_window import Ui_BuildNewProject





class ProjectBuilderManager(QObject):
    log: Signal = Signal(str)
    finished: Signal = Signal(bool)

    def __init__(self, parent: Optional[QObject] = None):
        super().__init__(parent)
        self.proc: Optional[Process] = None
        self.log_q: Optional[Queue] = None
        self.timer: QTimer = QTimer(self)

        _ = self.timer.timeout.connect(self._read_log)

    def start_building(self, cfg: Dict[str, Any]) -> None:
        if self.proc is not None and self.proc.is_alive():
            self.log.emit("[WARNING] Another build is already running!")
            return

        self.log_q = Queue()
        self.proc = Process(
            target=build_project,
            args=(cfg, self.log_q),
            daemon=True
        )
        self.proc.start()
        _ = self.timer.start(200)


    def _read_log(self) -> None:
        if self.log_q is None:
            return

        while not self.log_q.empty():
            try:
                msg = self.log_q.get_nowait()
                if msg is None:
                    self.timer.stop()
                    if self.proc is not None and self.proc.is_alive():
                        self.proc.join(timeout=2)
                    self.finished.emit(True)
                    break
                elif isinstance(msg, str):
                    self.log.emit(msg)
            except Exception as e:
                self.log.emit(f"[ERROR] Log read error: {e}")
                break

    def stop(self) -> None:
        if self.proc is not None and self.proc.is_alive():
            self.proc.terminate()
            _ = self.proc.join()
            self.log.emit("[WARNING] Build terminated by user")


class BuildWindow(QWidget, Ui_BuildNewProject):

    def __init__(self):
        super().__init__()
        self.setupUi(self)


        self.model_configs: List[Dict[str, Any]] = []
        self.model_dict: Dict[str, Dict[str, Any]] = {}
        self.current_model_config: Optional[Dict[str, Any]] = None


        self.builder_mgr = ProjectBuilderManager(self)
        _ = self.builder_mgr.log.connect(self.append_log)
        _ = self.builder_mgr.finished.connect(self.on_building_finished)


        _ = self.btn_select_path.clicked.connect(self.select_image_folder)
        _ = self.btn_start_building.clicked.connect(self.on_start_building)
        _ = self.btn_stop_building.clicked.connect(self.on_stop_building)


        self.load_model_configs()


        self.text_log.clear()
        self.append_log("Ready to build new project...")



    def load_model_configs(self) -> None:
        config_path = Path("model_config.json")

        if not config_path.exists():
            raise FileNotFoundError(f"Model config file not found: {config_path.resolve()}")

        try:
            with open(config_path, "r", encoding="utf-8") as f:
                json_cfg = json.load(f)

            self.model_configs = json_cfg.get("models", [])
            default_model = json_cfg.get("default_model", "")

            if not self.model_configs:
                raise ValueError("No models found in config")

            try:
                self.combo_algo.currentTextChanged.disconnect(self.on_model_changed)
            except (TypeError, RuntimeError):
                pass

            self.combo_algo.clear()
            self.model_dict.clear()

            for model in self.model_configs:
                display_name = model.get("display_name", model.get("name", "Unknown"))
                self.model_dict[display_name] = model
                self.combo_algo.addItem(display_name)

            self.combo_algo.currentTextChanged.connect(self.on_model_changed)

            default_idx = 0
            if default_model:
                for i, model in enumerate(self.model_configs):
                    if model.get("name") == default_model:
                        default_idx = i
                        break

            self.combo_algo.setCurrentIndex(default_idx)

            current_text = self.combo_algo.currentText()
            self.current_model_config = self.model_dict.get(current_text)

            self.append_log(f"[INFO] Loaded {len(self.model_configs)} models from config")

        except Exception as e:
            self.append_log(f"[ERROR] Failed to load config: {e}, using defaults")



    def on_model_changed(self, text: str) -> None:
        self.current_model_config = self.model_dict.get(text, {"name": text})
        if self.current_model_config:
            desc = self.current_model_config.get("description", "")
            self.append_log(f"[INFO] Selected: {text} - {desc}")



    def select_image_folder(self) -> None:
        folder = QFileDialog.getExistingDirectory(self, "Select Image Folder")
        if folder:
            self.line_image_path.setText(folder)
            count = self._count_images(folder)
            self.append_log(f"[INFO] Selected: {folder} ({count} images)")

    def _count_images(self, folder: str) -> int:
        valid_exts = {".jpg", ".jpeg", ".png", ".bmp", ".tiff", ".tif"}
        try:
            return sum(1 for f in os.listdir(folder)
                       if os.path.splitext(f)[1].lower() in valid_exts)
        except Exception:
            return 0

    def collect_cfg(self) -> Dict[str, Any]:
        return {
            "image_path": self.line_image_path.text().strip(),
            "project_name": self.line_project_name.text().strip(),
            "model": self.current_model_config or {"name": "Unknown"},
            "model_path": (self.current_model_config or {}).get("model_path", "")
        }




    def validate_cfg(self, cfg: Dict[str, Any]) -> Tuple[bool, str]:
        if not cfg["image_path"]:
            return False, "Please select an image folder!"

        if not os.path.exists(cfg["image_path"]):
            return False, f"Path does not exist: {cfg['image_path']}"

        if not cfg["project_name"]:
            return False, "Please enter a project name!"

        invalid_chars = '<>:"/\\|?*'
        if any(c in cfg["project_name"] for c in invalid_chars):
            return False, f"Project name contains invalid characters"

        if (Path("projects") / cfg["project_name"]).exists():
            return False, f"Project '{cfg['project_name']}' already exists!"

        return True, "OK"




    def on_start_building(self) -> None:
        cfg = self.collect_cfg()

        is_valid, msg = self.validate_cfg(cfg)
        if not is_valid:
            QMessageBox.warning(self, "Validation Failed", msg)
            return

        model_name = cfg["model"].get("display_name", cfg["model"].get("name", "Unknown"))

        reply = QMessageBox.question(
            self, "Confirm Build",
            f"Create project '{cfg['project_name']}' with model '{model_name}'?",
            QMessageBox.Yes | QMessageBox.No
        )

        if reply != QMessageBox.Yes:
            return

        self.text_log.clear()
        self.btn_start_building.setEnabled(False)
        self.btn_stop_building.setEnabled(True)
        self.append_log(f"[INFO] Starting build: {cfg['project_name']}")

        self.builder_mgr.start_building(cfg)

    def on_stop_building(self) -> None:
        self.builder_mgr.stop()
        self.btn_stop_building.setEnabled(False)

    def on_building_finished(self, success: bool) -> None:
        self.btn_start_building.setEnabled(True)
        self.btn_stop_building.setEnabled(False)
        if success:
            QMessageBox.information(self, "Success", "Project built successfully!")
        else:
            QMessageBox.critical(self, "Error", "Build failed! Check log for details.")


    def append_log(self, txt: str) -> None:
        self.text_log.append(txt)
        self.text_log.ensureCursorVisible()


def main():
    if sys.platform == 'win32':
        import multiprocessing
        multiprocessing.freeze_support()

    app = QApplication(sys.argv)
    window = BuildWindow()
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()