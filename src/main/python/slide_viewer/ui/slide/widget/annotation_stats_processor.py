from typing import Callable

from PyQt5.QtCore import QObject
from dataclasses import dataclass

from common_qt.util.qobjects_convert_util import ituples_to_qpoints
from slide_viewer.ui.common.metrics import calc_length, calc_geometry_area
from slide_viewer.ui.common.model import AnnotationModel, AnnotationStats


@dataclass
class AnnotationStatsProcessor(QObject):
    microns_per_pixel_provider: Callable[[], float]

    def __post_init__(self):
        QObject.__init__(self)

    def calc_stats(self, model: AnnotationModel) -> AnnotationStats:
        microns_per_pixel = self.microns_per_pixel_provider()
        # edit annotation model through tree deepable model interface
        # or make a copy and emit signal about changing annotation model
        if model.geometry.is_distinguishable_from_point():
            annotation_type = model.geometry.annotation_type
            points = ituples_to_qpoints(model.geometry.points)
            if annotation_type.has_length():
                length_px = calc_length(points[0], points[-1])
                length = length_px * microns_per_pixel
                length_text = f'length: {int(length)}\u00B5'
                return AnnotationStats(length_px=int(length_px), length=int(length), length_text=length_text)
            elif annotation_type.has_area():
                area_px = calc_geometry_area(model.geometry)
                area = area_px * microns_per_pixel ** 2
                area_text = f'area: {int(area)}\u00B5\u00B2'
                return AnnotationStats(area_px=int(area_px), area=int(area), area_text=area_text)
