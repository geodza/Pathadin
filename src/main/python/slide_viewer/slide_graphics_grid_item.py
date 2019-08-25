import os
from bisect import bisect_left
import typing
from concurrent.futures import ThreadPoolExecutor
from math import log

import openslide
from PyQt5 import QtGui, QtCore
from PyQt5.QtCore import QRectF, QSizeF, QPointF, QRect, Qt, QMutex, QMutexLocker, QPoint, QLineF
from PyQt5.QtGui import *
from PyQt5.QtWidgets import QGraphicsItem, QWidget, QStyleOptionGraphicsItem

from slide_viewer.common import pilimage_to_pixmap
from slide_viewer.config import debug, cell_size
from slide_viewer.slide_helper import SlideHelper


class SlideGraphicsGridItem(QGraphicsItem):
    def __init__(self, bounding_rect: QRectF, min_zoom, max_zoom, grid_size=(512, 512)):
        super().__init__()
        self.bounding_rect = bounding_rect
        self.grid_size = grid_size
        self.min_zoom = min_zoom
        self.max_zoom = max_zoom
        self.paint_called_count = 0
        self.update_grid_size(grid_size)

    def update_grid_size(self, grid_size):
        self.grid_size = grid_size
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

        current_zoom = 1 / painter.transform().m11()
        alpha = 255 - 250 * log(1 + current_zoom - 1 / self.max_zoom, 1 / self.min_zoom)

        qpen = QPen(QBrush(QColor(0, 0, 0, alpha)), 1)
        qpen.setCosmetic(True)
        painter.setPen(qpen)
        painter.drawLines(self.vertical_lines)
        painter.drawLines(self.horizontal_lines)
