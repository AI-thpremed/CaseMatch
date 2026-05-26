import sys
import os
from pathlib import Path
from PySide6.QtWidgets import (
    QApplication, QWidget, QMessageBox, QFileDialog
)
from PySide6.QtCore import QObject, QTimer, Signal
from multiprocessing import Process, Queue
from ui_manage_window import Ui_ManageProject
from manage_project_worker import update_worker


class IndexManager(QObject):
    log = Signal(str)
    finished = Signal(bool)
    progress = Signal(int)

    def __init__(self):
        super().__init__()
        self.proc = None
        self.timer = QTimer()
        self.timer.timeout.connect(self._read_log)

    def start_rebuild(self, project_path: str):
        if self.proc and self.proc.is_alive():
            self.log.emit("[WARNING] Another operation is already running!")
            return

        self.log_q = Queue()
        self.proc = Process(
            target=rebuild_worker,
            args=(project_path, self.log_q),
            daemon=True
        )
        self.proc.start()
        self.timer.start(200)

    def start_update(self, project_path: str):
        if self.proc and self.proc.is_alive():
            self.log.emit("[WARNING] Another operation is already running!")
            return

        self.log_q = Queue()
        self.proc = Process(
            target=update_worker,
            args=(project_path, self.log_q),
            daemon=True
        )
        self.proc.start()
        self.timer.start(200)



    def _read_log(self):
        while not self.log_q.empty():
            msg = self.log_q.get()
            if msg is None:
                self.timer.stop()
                self.finished.emit(True)
                if self.proc:
                    self.proc.join()
                break
            self.log.emit(str(msg))

    def stop(self):
        if self.proc and self.proc.is_alive():
            self.proc.terminate()
            self.proc.join()
            self.log.emit("[WARNING] Operation terminated by user")


class ManageWindow(QWidget, Ui_ManageProject):
    def __init__(self):
        super().__init__()
        self.setupUi(self)


        self.index_mgr = IndexManager()
        self.index_mgr.log.connect(self.append_log)
        self.index_mgr.finished.connect(self.on_operation_finished)


        self.btn_load.clicked.connect(self.on_load_project)
        self.btn_update_index.clicked.connect(self.on_update_index)


        self.current_project_path = None


        self.text_log.clear()
        self.append_log("Ready. Please load a project first.")

    def on_load_project(self):
        folder = QFileDialog.getExistingDirectory(
            self,
            "Select Project Folder",
            options=QFileDialog.ShowDirsOnly
        )

        if not folder:
            return


        config_file = Path(folder) / "project_config.json"
        if not config_file.exists():
            QMessageBox.warning(
                self,
                "Invalid Project",
                "Selected folder is not a valid project (missing project_config.json)"
            )
            return

        self.line_project_path.setText(folder)
        self.current_project_path = folder
        self.append_log(f"[INFO] Project loaded: {folder}")


        try:
            import json
            with open(config_file, 'r') as f:
                config = json.load(f)
            self.append_log(f"[INFO] Project name: {config.get('project_name', 'Unknown')}")
            self.append_log(f"[INFO] Image path: {config.get('image_path', 'Unknown')}")
            self.append_log(f"[INFO] Model path: {config.get('model', {}).get('model_path', 'Unknown')}")
            self.append_log(f"[INFO] Backbone: {config.get('model', {}).get('backbone', 'Unknown')}")
            self.append_log(f"[INFO] Image count: {config.get('vectorized_count', 0)}")
        except Exception as e:
            self.append_log(f"[WARNING] Could not read project config: {e}")


    def on_update_index(self):
        if not self._check_project_loaded():
            return

        self._disable_buttons()
        self.append_log("[INFO] Starting index update operation...")
        self.index_mgr.start_update(self.current_project_path)

    def _check_project_loaded(self) -> bool:
        if not self.current_project_path:
            QMessageBox.warning(
                self,
                "No Project Loaded",
                "Please load a project first!"
            )
            return False
        return True

    def _disable_buttons(self):
        self.btn_update_index.setEnabled(False)

    def _enable_buttons(self):
        self.btn_update_index.setEnabled(True)

    def on_operation_finished(self, success: bool):
        self._enable_buttons()
        if success:
            self.append_log("[INFO] Operation completed successfully")
        else:
            self.append_log("[ERROR] Operation failed or was interrupted")

    def append_log(self, txt: str):
        self.text_log.append(txt)
        self.text_log.ensureCursorVisible()



if __name__ == "__main__":
    app = QApplication(sys.argv)


    os.makedirs("projects", exist_ok=True)

    window = ManageWindow()
    window.show()
    sys.exit(app.exec())