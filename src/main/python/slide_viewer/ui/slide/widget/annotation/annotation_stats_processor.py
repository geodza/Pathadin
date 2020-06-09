from typing import Callable

from PyQt5.QtCore import QObject
from dataclasses import dataclass

from common.log_utils import log
from common_qt.util.qobjects_convert_util import ituples_to_qpoints
from common_qt.metrics import calc_line_length, calc_rect_area, calc_ellipse_area, calc_polygon_area, \
    are_points_distinguishable
from annotation.annotation_type import AnnotationType
from annotation.model import AnnotationModel, AnnotationStats, AnnotationGeometry


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

@dataclass
class AnnotationStatsProcessor(QObject):
    microns_per_pixel_provider: Callable[[], float]

    def __post_init__(self):
        QObject.__init__(self)

    def calc_stats(self, model: AnnotationModel) -> AnnotationStats:
        microns_per_pixel = self.microns_per_pixel_provider()
        # edit annotation model through tree deepable model interface
        # or make a copy and emit signal about changing annotation model
        if are_points_distinguishable(model.geometry.points):
            annotation_type = model.geometry.annotation_type
            points = ituples_to_qpoints(model.geometry.points)
            if annotation_type.has_length():
                length_px = calc_line_length(points[0], points[-1])
                length = length_px * microns_per_pixel
                length_text = f'length: {int(length)}\u00B5'
                return AnnotationStats(text=length_text, length_px=int(length_px), length=int(length), length_text=length_text)
            elif annotation_type.has_area():
                area_px = calc_geometry_area(model.geometry)
                area = area_px * microns_per_pixel ** 2
                area_text = f'area: {int(area)}\u00B5\u00B2'
                return AnnotationStats(text=area_text, area_px=int(area_px), area=int(area), area_text=area_text)

