from typing import Optional, ClassVar, List, Union, Tuple

from PyQt5.QtCore import QPoint, QPointF
from PyQt5.QtGui import QColor
from pydantic import BaseModel

from slide_viewer.ui.model.annotation_type import AnnotationType


class AnnotationFigureModel():
    type: AnnotationType
    points: List[QPoint]
    color: QColor
    hidden: bool


class AnnotationTextModel:
    text: str
    background_color: QColor
    hidden: bool


class TextGraphicsViewConfig(BaseModel):
    snake_case_name: ClassVar = 'text_graphics_view_config'
    display_attrs: List[str] = ['label']
    hidden: bool = False
    background_color: str =  '#32cd32'


class FigureGraphicsViewConfig(BaseModel):
    snake_case_name: ClassVar = 'figure_graphics_view_config'
    hidden: bool = False
    color: str = '#32cd32'


def are_points_distinguishable(points: List):
    return len(points) >= 2 and points[0] != points[1]


class AnnotationGeometry(BaseModel):
    annotation_type: AnnotationType
    origin_point: Tuple[int, int]
    points: List[Tuple[int, int]]

    def is_distinguishable_from_point(self) -> bool:
        return are_points_distinguishable(self.points)


class AnnotationStats(BaseModel):
    # __slots__ = ['area', 'area_px', 'length', 'length_px', 'prop2']  # for pycharm hints only
    area: Optional[int]
    area_px: Optional[int]
    length: Optional[int]
    length_px: Optional[int]
    # dd: OrderedDict = OrderedDict()
    # prop2: int = attr.ib()
