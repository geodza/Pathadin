import typing
from math import log

from PyQt5 import QtGui, QtCore
from PyQt5.QtCore import QRectF, QSizeF, QPointF, QRect, Qt, QMutex, QMutexLocker, QPoint, QLineF
from PyQt5.QtGui import *
from PyQt5.QtWidgets import QGraphicsItem, QWidget, QStyleOptionGraphicsItem


class SlideGraphicsGridItem(QGraphicsItem):
    def __init__(self, bounding_rect: QRectF, min_scale, max_scale, grid_size=(512, 512)):
        super().__init__()
        self.bounding_rect = bounding_rect
        # self.setFlag(QGraphicsItem.ItemIsMovable, True)
        # self.setFlag(QGraphicsItem.ItemIsSelectable, True)
        self.grid_size = grid_size
        self.min_scale = min_scale
        self.max_scale = max_scale
        self.paint_called_count = 0
        self.update_lines()
        self.setCacheMode(QGraphicsItem.DeviceCoordinateCache)

    def update_lines(self):
        top, left, bottom, right = self.bounding_rect.top(), self.bounding_rect.left(), self.bounding_rect.bottom(), self.bounding_rect.right()
        w, h = self.grid_size[0], self.grid_size[1]
        vertical_lines_count = int(self.boundingRect().width() // self.grid_size[0] + 1)
        horizontal_lines_count = int(self.boundingRect().height() // self.grid_size[1] + 1)
        self.vertical_lines = [QLineF(left + i * w, top, left + i * w, bottom) for i in range(vertical_lines_count)]
        self.horizontal_lines = [QLineF(left, top + i * h, right, top + i * h) for i in range(horizontal_lines_count)]

    def boundingRect(self) -> QtCore.QRectF:
        return self.bounding_rect

    def paint(self, painter: QtGui.QPainter, option: QStyleOptionGraphicsItem,
              widget: typing.Optional[QWidget] = ...) -> None:
        painter.save()
        self.paint_called_count += 1
        # painter.setClipRect(option.exposedRect)

        current_scale = 1 / painter.transform().m11()
        alpha = 255 - 250 * log(1 + current_scale - 1 / self.max_scale, 1 / self.min_scale)

        qpen = QPen(QBrush(QColor(0, 0, 0, alpha)), 1)
        qpen.setCosmetic(True)
        painter.setPen(qpen)
        painter.drawLines(self.vertical_lines)
        painter.drawLines(self.horizontal_lines)
