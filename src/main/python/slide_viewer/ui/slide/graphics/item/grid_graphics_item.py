import typing
from math import log

from PyQt5 import QtGui, QtCore
from PyQt5.QtCore import QRectF, QLineF
from PyQt5.QtGui import *
from PyQt5.QtWidgets import QGraphicsItem, QWidget, QStyleOptionGraphicsItem
from dataclasses import dataclass, field


@dataclass
class GridGraphicsItem(QGraphicsItem):
    bounding_rect: QRectF
    min_scale: float
    max_scale: float
    grid_size: typing.Tuple[int, int] = (512, 512)
    vertical_lines: typing.List[QLineF] = field(init=False, default_factory=list)
    horizontal_lines: typing.List[QLineF] = field(init=False, default_factory=list)
    paint_called_count: int = field(init=False, default=0)

    def __post_init__(self):
        super().__init__()
        self.setCacheMode(QGraphicsItem.DeviceCoordinateCache)
        self.update_lines()

    def update_lines(self) -> None:
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

        # print(int(alpha))
        # qpen = QPen(QBrush(QColor(0, 0, 0, int(alpha))), 1)
        qpen = QPen(QBrush(QColor(0, 0, 0, 100)), 1)
        qpen.setCosmetic(True)
        painter.setPen(qpen)
        painter.drawLines(self.vertical_lines)
        painter.drawLines(self.horizontal_lines)
        painter.restore()
