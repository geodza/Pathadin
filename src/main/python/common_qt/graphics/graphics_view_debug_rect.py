from PyQt5.QtCore import Qt
from PyQt5.QtGui import QPen, QBrush, QColor
from PyQt5.QtWidgets import QGraphicsRectItem, QGraphicsView


class GraphicsViewDebugRect(QGraphicsRectItem):

    def __init__(self, view: QGraphicsView) -> None:
        super().__init__()
        pen = QPen(QBrush(Qt.magenta), 50)
        brush = QBrush(QColor.fromRgb(0, 0, 80, 110))
        item_rect = view.sceneRect()
        self.setRect(item_rect)
        self.setPen(pen)
        self.setBrush(brush)
        self.setZValue(-1)
