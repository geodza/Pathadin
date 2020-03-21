from typing import Any, Optional

from PyQt5.QtCore import QPointF, QRectF, pyqtSignal, QObject, QPoint
from PyQt5.QtGui import *
from PyQt5.QtWidgets import QGraphicsItemGroup, QGraphicsItem
from dataclasses import dataclass, field, InitVar

from slide_viewer.ui.slide.graphics.item.annotation.annotation_figure_graphics_item import AnnotationFigureGraphicsItem, \
    AnnotationFigureGraphicsModel
from slide_viewer.ui.slide.graphics.item.annotation.annotation_text_graphics_item import AnnotationTextGraphicsItem, \
    AnnotationTextGraphicsModel
from slide_viewer.ui.slide.widget.interface.scale_view_provider import ScaleProvider


@dataclass
class AnnotationGraphicsModel:
    pos: QPoint
    figure_model: AnnotationFigureGraphicsModel
    text_model: AnnotationTextGraphicsModel
    figure_hidden: bool
    text_hidden: bool


class AnnotationGraphicsItemSignals(QObject):
    posChanged = pyqtSignal(str, QPoint)
    removedFromScene = pyqtSignal(str)

    def __init__(self, parent: Optional[QObject] = None) -> None:
        super().__init__(parent)


@dataclass
class AnnotationGraphicsItem(QGraphicsItemGroup):
    id: str
    scale_provider: ScaleProvider
    model: InitVar[Optional[AnnotationGraphicsModel]]
    is_in_progress: bool
    # removed_from_scene_callback: Callable[[str], None]
    figure: AnnotationFigureGraphicsItem = None
    text: AnnotationTextGraphicsItem = None

    signals: AnnotationGraphicsItemSignals = field(default_factory=AnnotationGraphicsItemSignals)

    def __post_init__(self, model: AnnotationGraphicsModel):
        QGraphicsItemGroup.__init__(self)
        self.figure = AnnotationFigureGraphicsItem(self.scale_provider)
        self.figure.setParentItem(self)
        self.text = AnnotationTextGraphicsItem()
        self.text.setParentItem(self)
        self.setFlag(QGraphicsItem.ItemSendsGeometryChanges)
        self.setFlag(QGraphicsItem.ItemSendsScenePositionChanges)

        if model:
            self.set_model(model)

    def set_model(self, model: AnnotationGraphicsModel) -> None:
        new_pos = model.pos
        if new_pos != self.pos():
            self.prepareGeometryChange()
            self.setPos(new_pos)
        self.figure.set_model(model.figure_model)
        self.figure.setVisible(not model.figure_hidden)
        self.figure.update()
        self.text.set_model(model.text_model)
        self.text.setPos(self.figure.boundingRect().center())
        self.text.setVisible(not model.text_hidden)
        self.text.update()
        self.update()

    def update(self, rect: QRectF = QRectF()) -> None:
        self.setFlag(QGraphicsItem.ItemIsMovable, not self.is_in_progress)
        self.setFlag(QGraphicsItem.ItemIsSelectable, not self.is_in_progress)
        # self.setCursor(Qt.ClosedHandCursor if not self.is_in_progress else Qt.ArrowCursor)
        self.text.update()
        self.figure.update()
        super().update(rect)

    def itemChange(self, change: QGraphicsItem.GraphicsItemChange, value: Any) -> Any:
        if change == QGraphicsItem.ItemSelectedHasChanged:
            self.figure.setSelected(value)
            self.update()
        if change == QGraphicsItem.ItemPositionChange:
            if isinstance(value, QPointF):
                value = value.toPoint()
            self.signals.posChanged.emit(self.id, value)
            return value
        elif change == QGraphicsItem.ItemPositionHasChanged:
            return super().itemChange(change, value)
        elif change == QGraphicsItem.ItemSceneHasChanged:
            if not value:
                self.signals.removedFromScene.emit(self.id)
                return
            return super().itemChange(change, value)
        else:
            return super().itemChange(change, value)

    def boundingRect(self) -> QRectF:
        return self.figure.boundingRect()

    def shape(self) -> QPainterPath:
        return self.figure.shape()
