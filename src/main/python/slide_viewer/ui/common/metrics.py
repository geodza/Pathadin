import math
import typing

from PyQt5.QtCore import QPoint, QRect
from PyQt5.QtGui import QVector2D

# def calc_polygon_area(polygon: QPolygonF):
#     area = 0
#     for i in range(polygon.size()):
#         pi, pj = polygon[i], polygon[i - 1]
#         area += (pj.x() + pi.x()) * (pj.y() - pi.y())
#     return abs(area) / 2
from common_qt.qobjects_convert_util import ituples_to_qpoints
from slide_viewer.ui.common.model import AnnotationGeometry
from slide_viewer.ui.common.annotation_type import AnnotationType


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


def calc_length(p1: QPoint, p2: QPoint) -> float:
    return QVector2D(p2 - p1).length()


def calc_geometry_area(geometry: AnnotationGeometry) -> float:
    annotation_type = geometry.annotation_type
    points = ituples_to_qpoints(geometry.points)
    if annotation_type == AnnotationType.RECT:
        area_px = calc_rect_area(points[0], points[-1])
    elif annotation_type == AnnotationType.ELLIPSE:
        area_px = calc_ellipse_area(points[0], points[-1])
    elif annotation_type == AnnotationType.POLYGON:
        area_px = calc_polygon_area(points)
    else:
        raise ValueError(f'Unexpected annotation_type: {annotation_type}')
    return area_px
