import typing

from PyQt5.QtCore import QPointF
from PyQt5.QtGui import QColor

from slide_viewer.ui.annotation.annotation_type import AnnotationType


class AnnotationData:

    def __init__(self, points: typing.List[QPointF] = None, name: str = None, pen_color: QColor = None,
                 text_background_color: QColor = None, annotation_type: AnnotationType = None) -> None:
        super().__init__()
        self.points = points
        self.name = name
        self.pen_color = pen_color
        self.text_background_color = text_background_color
        self.annotation_type = annotation_type