from typing import Optional

from PyQt5.QtCore import Qt, QMarginsF
from PyQt5.QtGui import QColor
from PyQt5.QtWidgets import QGraphicsItem, QGraphicsRectItem, QGraphicsItemGroup, \
    QGraphicsTextItem, QApplication
from dataclasses import dataclass, InitVar


@dataclass
class AnnotationTextGraphicsModel:
    text: Optional[str]
    background_color: QColor = QColor('green')


@dataclass
class AnnotationTextGraphicsItem(QGraphicsItemGroup):
    model: InitVar[Optional[AnnotationTextGraphicsModel]] = None

    def __post_init__(self, model: Optional[AnnotationTextGraphicsModel]):
        QGraphicsItemGroup.__init__(self)
        self.background = QGraphicsRectItem(self)
        self.background.setAcceptHoverEvents(False)
        self.background.setFlag(QGraphicsItem.ItemIgnoresTransformations)
        self.background.setAcceptedMouseButtons(Qt.NoButton)

        self.text_item = QGraphicsTextItem(self)
        self.text_item.setAcceptHoverEvents(False)
        self.text_item.setFlag(QGraphicsItem.ItemIgnoresTransformations)
        self.text_item.setAcceptedMouseButtons(Qt.NoButton)
        self.text_item.setFont(create_annotation_text_font())

        self.setFlag(QGraphicsItem.ItemSendsGeometryChanges)
        if model:
            self.set_model(model)

    def set_model(self, model: AnnotationTextGraphicsModel):
        brush = self.background.brush()
        brush.setStyle(Qt.SolidPattern)
        brush.setColor(model.background_color)
        self.background.setBrush(brush)
        if model.text != self.text_item.toHtml():
            self.prepareGeometryChange()
            self.text_item.setHtml(model.text)
            self.background.setRect(self.text_item.boundingRect() + QMarginsF(4, 4, 4, 4))
        self.update()


def create_annotation_text_font():
    f = QApplication.font()
    f.setPointSize(int(f.pointSize() * 1.2))
    return f
