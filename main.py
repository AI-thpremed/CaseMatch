# -*- coding: utf-8 -*-

import os

# 这必须在任何 torch 相关导入之前
os.environ["TORCHDYNAMO"] = "0"
os.environ["TORCH_DYNAMO"] = "0"  # 两种写法都加上
os.environ["PYTORCH_JIT"] = "0"


import sys
import io

# ===== 第一优先级：设置 DLL 路径 =====
def setup_dll_paths():
    if getattr(sys, 'frozen', False):
        # 打包环境：在导入任何模块前就设置好路径
        base_path = getattr(sys, '_MEIPASS', os.path.dirname(os.path.abspath(sys.argv[0])))

        # torch lib 路径
        torch_lib = os.path.join(base_path, "torch", "lib")
        if os.path.exists(torch_lib) and hasattr(os, 'add_dll_directory'):
            os.add_dll_directory(torch_lib)
            # 注释掉这整个 with open 块
            # with open("C:\\temp\\dll_setup.txt", "w") as f:
            #     f.write(f"Added torch lib: {torch_lib}\n")

        # Qt 插件路径
        plugin_path = os.path.join(base_path, "PySide6", "qt-plugins")
        if os.path.exists(plugin_path) and hasattr(os, 'add_dll_directory'):
            os.add_dll_directory(plugin_path)
    else:
        # 开发环境：直接使用 conda 环境中的路径
        conda_torch_lib = r"G:\miniconda3\envs\pytorch_gpu\Lib\site-packages\torch\lib"
        if os.path.exists(conda_torch_lib) and hasattr(os, 'add_dll_directory'):
            os.add_dll_directory(conda_torch_lib)

# 立即执行！
setup_dll_paths()

os.environ['TORCH_DYNAMO'] = '0'

# ==== Nuitka/PyInstaller 通用路径修复 ====
def get_base_path():
    if getattr(sys, 'frozen', False):
        # Nuitka: sys.argv[0] 指向 exe
        # PyInstaller: _MEIPASS 指向临时解压目录
        return getattr(sys, '_MEIPASS', os.path.dirname(os.path.abspath(sys.argv[0])))
    return os.path.dirname(os.path.abspath(__file__))

base_path = get_base_path()

# ==== Qt 插件路径（必须在 Qt 导入前设置） ====
if getattr(sys, 'frozen', False):
    plugin_path = os.path.normpath(os.path.join(base_path, "PySide6", "qt-plugins"))
    if os.path.exists(plugin_path):
        os.environ["QT_PLUGIN_PATH"] = plugin_path
        os.environ["QT_QPA_PLATFORM_PLUGIN_PATH"] = plugin_path
        sys.path.append(plugin_path)
        if os.name == 'nt' and hasattr(os, 'add_dll_directory'):
            os.add_dll_directory(plugin_path)
        print(f"path: {plugin_path}")

# torch lib 路径（Nuitka 需要）
torch_lib = os.path.join(base_path, "torch", "lib")
if os.path.exists(torch_lib) and hasattr(os, 'add_dll_directory'):
    os.add_dll_directory(torch_lib)

from build_gui import BuildWindow
from manage_gui import ManageWindow
from retrieval_gui import RetrievalWindow
from PySide6.QtGui import QIcon


# Force UTF-8
def configure_encoding():
    # 检查 stdout 和 stderr 是否存在（打包后的 GUI 应用可能为 None）
    if sys.stdout is not None and hasattr(sys.stdout, 'encoding'):
        if sys.stdout.encoding != 'UTF-8':
            sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

    if sys.stderr is not None and hasattr(sys.stderr, 'encoding'):
        if sys.stderr.encoding != 'UTF-8':
            sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

    os.environ["PYTHONIOENCODING"] = "utf-8"
    os.environ["QT_DEBUG_PLUGINS"] = "1"


configure_encoding()

from PySide6.QtWidgets import QApplication, QMainWindow, QTabWidget, QMessageBox
from PySide6.QtUiTools import QUiLoader
from PySide6.QtCore import QTimer


def resource_path(relative_path):
    return os.path.join(get_base_path(), relative_path)

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("CaseMatch v1.0")
        self.resize(250, 300)
        self.setWindowIcon(QIcon(resource_path("images/logo.png")))
        self.tab_widget = QTabWidget()
        self.setCentralWidget(self.tab_widget)
        loader = QUiLoader()
        ui_path = resource_path("UI/introduction.ui")
        welcome_widget = loader.load(ui_path)
        self.tab_widget.addTab(welcome_widget, "Home")
        self.tab_widget.addTab(BuildWindow(), "Build Project")
        self.tab_widget.addTab(ManageWindow(), "Manage Project")
        self.tab_widget.addTab(RetrievalWindow(), "Image Retrieval")


def handle_exception(exc_type, exc_value, exc_traceback):
    QMessageBox.critical(
        None,
        "Fatal Error",
        f"Unhandled exception:\n\n{str(exc_value)}",
        QMessageBox.Ok
    )
    QTimer.singleShot(1000, lambda: sys.exit(1))


if __name__ == "__main__":
    import multiprocessing
    multiprocessing.freeze_support()  # ← 添加这一行

    sys.excepthook = handle_exception

    app = QApplication([])
    main_window = MainWindow()
    main_window.show()
    sys.exit(app.exec())