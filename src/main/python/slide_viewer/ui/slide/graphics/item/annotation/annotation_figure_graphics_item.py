import typing
from typing import Optional, List

from PyQt5 import QtGui
from PyQt5.QtCore import QRectF, Qt, QObject, pyqtSignal, QPoint, QMarginsF
from PyQt5.QtGui import *
from PyQt5.QtWidgets import QGraphicsItemGroup, QGraphicsPathItem, QGraphicsItem, QStyleOptionGraphicsItem, QWidget
from dataclasses import dataclass, InitVar, field

from slide_viewer.ui.model.annotation_type import AnnotationType
from slide_viewer.ui.slide.graphics.item.annotation.model import are_points_distinguishable
from slide_viewer.ui.slide.widget.interface.scale_view_provider import ScaleProvider


@dataclass
class AnnotationFigureGraphicsModel:
    annotation_type: AnnotationType
    points: List[QPoint]
    color: QColor = QColor('green')


class AnnotationFigureGraphicsItemSignals(QObject):
    modelChanged = pyqtSignal(AnnotationFigureGraphicsModel)

    def __init__(self, parent: Optional[QObject] = None) -> None:
        super().__init__(parent)


def build_path(annotation_type: AnnotationType, points: List[QPoint]):
    if are_points_distinguishable(points):
        path = QPainterPath()
        if annotation_type in (AnnotationType.RECT, AnnotationType.ELLIPSE, AnnotationType.LINE):
            first_point, last_point = points[0], points[-1]
            if annotation_type == AnnotationType.RECT:
                path.addRect(QRectF(first_point, last_point))
            elif annotation_type == AnnotationType.ELLIPSE:
                path.addEllipse(QRectF(first_point, last_point))
            elif annotation_type == AnnotationType.LINE:
                line_path = QPainterPath(first_point)
                line_path.lineTo(last_point)
                path.addPath(line_path)
        elif annotation_type == AnnotationType.POLYGON:
            path.addPolygon(QPolygonF(points))
    elif points:
        path = QPainterPath(points[0])
        path.lineTo(points[0])
    else:
        path = QPainterPath()
    return path


@dataclass
class AnnotationFigureGraphicsItem(QGraphicsItemGroup):
    scale_provider: ScaleProvider
    model: InitVar[Optional[AnnotationFigureGraphicsModel]] = None

    signals: AnnotationFigureGraphicsItemSignals = field(default_factory=AnnotationFigureGraphicsItemSignals)

    def __post_init__(self, model: Optional[AnnotationFigureGraphicsModel]):
        QGraphicsItemGroup.__init__(self)
        self.shape_item = QGraphicsPathItem(self)
        self.shape_item.setAcceptedMouseButtons(Qt.NoButton)
        self.setFlag(QGraphicsItem.ItemIsSelectable)
        self.setFlag(QGraphicsItem.ItemSendsGeometryChanges)
        if model:
            self.__set_model(model)

    def set_model(self, model: AnnotationFigureGraphicsModel):
        self.__set_model(model)
        self.signals.modelChanged.emit(model)

    def __set_model(self, model: AnnotationFigureGraphicsModel):
        self.prepareGeometryChange()
        path = build_path(model.annotation_type, model.points)
        self.shape_item.setPath(path)
        pen = self.shape_item.pen()
        pen.setColor(QColor(model.color))
        pen.setCosmetic(True)
        self.shape_item.setPen(pen)
        self.update()

    def update(self, rect: QRectF = QRectF()) -> None:
        pen = self.shape_item.pen()
        pen.setStyle(Qt.DotLine if self.isSelected() else Qt.SolidLine)
        new_pen_width = 5 if self.isSelected() else 3
        if new_pen_width != pen.width():
            self.prepareGeometryChange()
            pen.setWidth(new_pen_width)
        self.shape_item.setPen(pen)
        super().update(rect)

    def boundingRect(self) -> QRectF:
        pen_width = self.shape_item.pen().width()
        real_pen_width = pen_width / self.scale_provider.get_scale()
        margin = real_pen_width / 2
        r = self.shape_item.boundingRect() + QMarginsF(margin, margin, margin, margin)
        return r

    def shape(self) -> QPainterPath:
        shape_path = self.shape_item.shape()
        stroker = QPainterPathStroker()
        pen_width = self.shape_item.pen().width()
        real_pen_width = pen_width / self.scale_provider.get_scale()
        stroker.setWidth(real_pen_width)
        path = stroker.createStroke(shape_path)
        return path

    def paint(self, painter: QtGui.QPainter, option: QStyleOptionGraphicsItem,
              widget: typing.Optional[QWidget] = ...) -> None:
        # painter.save()
        # pen = QPen()
        # pen.setWidth(5)
        # pen.setColor(QColor("blue"))
        # pen.setCosmetic(True)
        # painter.setPen(pen)
        # painter.drawRect(self.boundingRect()+ QMarginsF(1, 1, 1, 1))
        # painter.restore()
        super().paint(painter, option, widget)
