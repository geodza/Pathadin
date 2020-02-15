import typing

from PyQt5.QtCore import QObject, pyqtSignal


class CloseNotifier(QObject):
    closing = pyqtSignal()

    def __init__(self, parent: typing.Optional[QObject]) -> None:
        super().__init__(parent)
