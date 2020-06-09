import math
import typing
from typing import List

from PyQt5.QtCore import QPoint, QRect
from PyQt5.QtGui import QVector2D


def calc_polygon_area(points: typing.List[QPoint]) -> float:
    area = 0
    for i in range(len(points)):
        pi, pj = points[i], points[i - 1]
        area += (pj.x() + pi.x()) * (pj.y() - pi.y())
    return abs(area) / 2


def calc_rect_area(p1: QPoint, p2: QPoint) -> float:
    rect = QRect(p1, p2)
    return abs(rect.width() * rect.height())


def calc_ellipse_area(p1: QPoint, p2: QPoint) -> float:
    return calc_rect_area(p1, p2) * math.pi / 4


def calc_line_length(p1: QPoint, p2: QPoint) -> float:
    return QVector2D(p2 - p1).length()


def are_points_distinguishable(points: List):
	return len(points) >= 2 and points[0] != points[1]