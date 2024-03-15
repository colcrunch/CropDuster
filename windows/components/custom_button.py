from PySide6.QtGui import QKeyEvent
from PySide6.QtWidgets import QPushButton

class CustomButton(QPushButton):
    def __init__(self, text=None, icon=None):
        super().__init__(text)
        if icon:
            super().setIcon(icon)

    def keyPressEvent(self, event: QKeyEvent) -> None:
        event.ignore()