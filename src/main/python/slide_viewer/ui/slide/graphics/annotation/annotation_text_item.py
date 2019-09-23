import typing

from PyQt5.QtCore import QRectF, Qt
from PyQt5.QtGui import QPainterPath, QPolygonF
from PyQt5.QtWidgets import QGraphicsSimpleTextItem, QGraphicsItem, QGraphicsRectItem, QGraphicsItemGroup

from slide_viewer.ui.slide.graphics.annotation.annotation_utls import create_annotation_text_brush, \
    create_annotation_text_font, create_annotation_text_margins


class AnnotationTextItem(QGraphicsItemGroup):

    def __init__(self, parent: typing.Optional[QGraphicsItem] = None) -> None:
        super().__init__(parent)

        self.background = QGraphicsRectItem(self)
        self.background.setBrush(create_annotation_text_brush())
        self.background.setFlag(QGraphicsItem.ItemIgnoresTransformations, True)
        self.background.setAcceptedMouseButtons(Qt.NoButton)

        self.text = QGraphicsSimpleTextItem(self)
        self.text.setAcceptHoverEvents(False)
        self.text.setFlag(QGraphicsItem.ItemIgnoresTransformations, True)
        self.text.setFont(create_annotation_text_font())
        self.text.setAcceptedMouseButtons(Qt.NoButton)

        self.setFlag(QGraphicsItem.ItemSendsGeometryChanges)

    def set_text(self, text):
        self.prepareGeometryChange()
        self.text.setText(text)
        self.background.setRect(self.text.boundingRect() + create_annotation_text_margins())

    def boundingRect(self) -> QRectF:
        rect = self.background.rect()
        # return self.account_ignore_transformation(rect).boundingRect()
        return rect

    def shape(self) -> QPainterPath:
        shape = self.background.shape()
        return self.account_ignore_transformation(shape)
        # return shape

    def account_ignore_transformation(self, shape):
        if not isinstance(shape, QPainterPath):
            path = QPainterPath()
            path.addPolygon(QPolygonF(shape))
            shape = path
        view = self.scene().views()[0]
        transform = view.viewportTransform()
        shape_view = self.background.deviceTransform(transform).map(shape)
        shape_scene = view.mapToScene(shape_view)
        shape_item_sized = self.background.mapFromScene(shape_scene)
        # print(
        #     f'shape: {shape.boundingRect()} shape_view: {shape_view.boundingRect()} shape_scene: {shape_scene.boundingRect()} shape_sized: {shape_item_sized.boundingRect()}')
        return shape_item_sized
