import typing

from PyQt5.QtCore import QTimer, QObject


class AlmostImmediateTimer(QTimer):
    def __init__(self, parent: QObject, callback) -> None:
        super().__init__(parent)
        self.setInterval(0)
        self.setSingleShot(True)
        self.timeout.connect(callback)
