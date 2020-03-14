from typing import Tuple, List, Optional

from PyQt5 import QtGui, QtCore
from PyQt5.QtCore import QRectF, QLineF
from PyQt5.QtGui import *
from PyQt5.QtWidgets import QGraphicsItem, QWidget, QStyleOptionGraphicsItem
from dataclasses import dataclass, field


@dataclass
class GridGraphicsItem(QGraphicsItem):
    bounding_rect: QRectF
    grid_size: Tuple[int, int] = (512, 512)
    vertical_lines: List[QLineF] = field(init=False, default_factory=list)
    horizontal_lines: List[QLineF] = field(init=False, default_factory=list)
    paint_called_count: int = field(init=False, default=0)

    def __post_init__(self):
        super().__init__()
        self.setCacheMode(QGraphicsItem.DeviceCoordinateCache)
        self.update_lines()

    def update_lines(self) -> None:
        top, left, bottom, right = self.bounding_rect.top(), self.bounding_rect.left(), self.bounding_rect.bottom(), self.bounding_rect.right()
        w, h = self.grid_size[0], self.grid_size[1]
        vertical_lines_count = int(self.boundingRect().width() // w + 1)
        horizontal_lines_count = int(self.boundingRect().height() // h + 1)
        self.vertical_lines = [QLineF(left + i * w, top, left + i * w, bottom) for i in range(vertical_lines_count)]
        self.horizontal_lines = [QLineF(left, top + i * h, right, top + i * h) for i in range(horizontal_lines_count)]

    def boundingRect(self) -> QtCore.QRectF:
        return self.bounding_rect

    def paint(self, painter: QtGui.QPainter, option: QStyleOptionGraphicsItem,
              widget: Optional[QWidget] = ...) -> None:
        painter.save()
        self.paint_called_count += 1
        # print(self.paint_called_count)

        current_scale = painter.transform().m11()
        grid_size_scene = self.grid_size
        grid_size_view = (grid_size_scene[0] * current_scale, grid_size_scene[1] * current_scale)
        grid_size_view_min = min(*grid_size_view)
        if grid_size_view_min <= 1:
            alpha = 0
        elif grid_size_view_min <= 10:
            a = 100 / (10 - 1)
            b = -a
            alpha = a * grid_size_view_min + b
        else:
            alpha = 100
        # print("alpha: {}".format(alpha))
        # print("current_scale: {}, grid_size_view: {}, alpha: {}".format(current_scale, grid_size_view, alpha))
        qpen = QPen(QBrush(QColor(0, 0, 0, int(alpha))), 1)
        qpen.setCosmetic(True)
        painter.setPen(qpen)
        painter.drawLines(self.vertical_lines)
        painter.drawLines(self.horizontal_lines)
        painter.restore()
