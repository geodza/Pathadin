from PyQt5.QtCore import QEvent, Qt
from PyQt5.QtGui import QKeyEvent


class KeyPressEventUtil:
    @staticmethod
    def is_enter(event: QEvent) -> bool:
        return isinstance(event, QKeyEvent) and event.key() in (Qt.Key_Enter, Qt.Key_Return)

    @staticmethod
    def is_esc(event: QEvent) -> bool:
        return isinstance(event, QKeyEvent) and event.key() == Qt.Key_Escape

    @staticmethod
    def is_delete(event: QEvent) -> bool:
        return isinstance(event, QKeyEvent) and event.key() == Qt.Key_Delete
