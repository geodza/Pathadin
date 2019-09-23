from PyQt5.QtCore import Qt
from PyQt5.QtGui import QPen, QBrush, QColor
from PyQt5.QtWidgets import QGraphicsRectItem, QGraphicsItem


class SlideGraphicsDebugItemRect(QGraphicsRectItem):

    def __init__(self, parent: QGraphicsItem) -> None:
        super().__init__(parent)
        pen = QPen(QBrush(Qt.darkCyan), 50)
        brush = QBrush(QColor.fromRgb(255, 0, 0, 150))
        item_rect = parent.boundingRect()
        self.setPen(pen)
        self.setBrush(brush)
        self.setRect(item_rect)
        self.setZValue(100)
