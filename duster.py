import sys
import os

from PySide6.QtWidgets import QApplication

from windows.main_window import MainWindow

__version__ = '0.0.1'

def resource_path(relative_path):
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")

    return os.path.join(base_path, relative_path)

if __name__ == "__main__":
    icon_path = resource_path("window_icon.png")
    app = QApplication(sys.argv)
    window = MainWindow(__version__, icon_path)
    window.show()
    sys.exit(app.exec())