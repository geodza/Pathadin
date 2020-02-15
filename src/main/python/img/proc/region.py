import typing
from typing import Tuple, Optional

from PIL import Image
from PyQt5.QtGui import QPolygon

from img.pos import ituple, ituples
from slide_viewer.cache_config import gcached
from slide_viewer.common.slide_helper import SlideHelper
from common_qt.qobjects_convert_util import ituple_to_qpoint, qpoint_to_ituple, ituples_to_qpoints, \
    qpoints_to_ituples
from slide_viewer.ui.model.annotation_type import AnnotationType


class RegionData(typing.NamedTuple):
    img_path: str
    level: typing.Optional[int] = None
    origin_point: typing.Optional[typing.Tuple[int, int]] = None
    points: typing.Optional[typing.Tuple[typing.Tuple[int, int], ...]] = None
    annotation_type: AnnotationType = AnnotationType.RECT


def read_region(data: RegionData) -> Image.Image:
    if data.points is not None and data.origin_point is not None:
        polygon = QPolygon([ituple_to_qpoint(p) for p in data.points])
        top_left = ituple_to_qpoint(data.origin_point) + polygon.boundingRect().topLeft()
        pos = qpoint_to_ituple(top_left)
        size = polygon.boundingRect().size()
        size = (size.width(), size.height())
        return load_region(data.img_path, pos, data.level, size)
    else:
        return load_region(data.img_path)


@gcached
def load_region(img_path: str, pos: Tuple[int, int] = (0, 0), level: Optional[int] = None,
                size: Tuple[int, int] = None) -> Image.Image:
    sh = SlideHelper(img_path)
    if level is None or level == "":
        level = sh.get_levels()[min(2, len(sh.get_levels()) - 1)]
    level = int(level)
    if level < 0:
        level = sh.get_levels()[-level]
    # TODO add literals for level like MAX_LEVEL, AUTO_LEVEL(about memory considerations)
    # print(f"load_region on level: {level}")
    level_downsample = sh.get_downsample_for_level(level)
    if size is not None:
        size = (size[0] / level_downsample, size[1] / level_downsample)
    region = sh.read_region_pilimage(pos, level, size)
    return region


def ituples_to_polygon_ituples(points: ituples) -> ituples:
    qpoints = tuple(ituples_to_qpoints(points))
    top_left = QPolygon(qpoints).boundingRect().topLeft()
    qpoints0 = [p - top_left for p in qpoints]
    points0 = tuple(qpoints_to_ituples(qpoints0))
    return points0


def deshift_points(points: typing.Iterable[ituple], origin_point: ituple) -> ituples:
    origin_point_deshifted = [(p[0] - origin_point[0], p[1] - origin_point[1]) for p in points]
    left = min(origin_point_deshifted, key=lambda p: p[0])
    top = min(origin_point_deshifted, key=lambda p: p[1])
    new_origin_point = (left[0], top[1])
    first_point_shifted = [(p[0] - new_origin_point[0], p[1] - new_origin_point[1]) for p in origin_point_deshifted]
    return tuple(first_point_shifted)


def rescale_points(points: typing.Iterable[ituple], sx: float, sy: float) -> ituples:
    rescaled_points = [(int(p[0] * sx), int(p[1] * sy)) for p in points]
    return tuple(rescaled_points)
