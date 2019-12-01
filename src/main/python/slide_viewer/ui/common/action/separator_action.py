from PyQt5.QtCore import QObject
from PyQt5.QtWidgets import QAction


class SeparatorAction(QAction):
    def __init__(self, parent: QObject) -> None:
        super().__init__(parent)
        self.setSeparator(True)
