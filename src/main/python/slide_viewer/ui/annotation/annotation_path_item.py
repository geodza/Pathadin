import typing
from typing import List

from PyQt5.QtCore import QPointF, QMarginsF, QRectF, Qt
from PyQt5.QtGui import *
from PyQt5.QtWidgets import QGraphicsItemGroup, QGraphicsPolygonItem, QGraphicsPathItem, QGraphicsItem

from slide_viewer.ui.annotation.annotation_text_item import AnnotationTextItem
from slide_viewer.ui.annotation.annotation_utls import create_annotation_pen, create_annotation_text_margins
from slide_viewer.ui.annotation.annotation_data import AnnotationData
from slide_viewer.ui.annotation.annotation_type import AnnotationType


class AnnotationPathItem(QGraphicsItemGroup):
    def __init__(self, annotation_data: AnnotationData = None, microns_per_pixel=1):
        super().__init__()
        self.microns_per_pixel = microns_per_pixel
        self.shape_item = QGraphicsPathItem(self)
        self.annotation_text = AnnotationTextItem(self)
        self.annotation_data: AnnotationData = annotation_data
        self.shape_item.setAcceptedMouseButtons(Qt.NoButton)
        self.annotation_text.text.setAcceptedMouseButtons(Qt.NoButton)
        self.annotation_text.background.setAcceptedMouseButtons(Qt.NoButton)
        # self.setAcceptedMouseButtons(Qt.NoButton)
        # self.setFlag(QGraphicsItem.ItemIsMovable, True)
        # self.setFlag(QGraphicsItem.ItemIsSelectable, True)
        self.setFlag(QGraphicsItem.ItemSendsGeometryChanges)
        self.update()

    def set_data(self, annotation_data: AnnotationData):
        self.annotation_data = annotation_data
        self.update()

    def update(self, rect: QRectF = QRectF()) -> None:
        if self.annotation_data and len(self.annotation_data.points) >= 2:
            self.update_shape()
            self.update_text()
            self.update_style()
        super().update(rect)

    def update_shape(self):
        self.prepareGeometryChange()
        path = QPainterPath()
        if self.annotation_data.annotation_type in (AnnotationType.RECT, AnnotationType.ELLIPSE, AnnotationType.LINE):
            p1 = self.annotation_data.points[0]
            p2 = self.annotation_data.points[-1]
            if self.annotation_data.annotation_type == AnnotationType.RECT:
                path.addRect(QRectF(p1, p2))
            elif self.annotation_data.annotation_type == AnnotationType.ELLIPSE:
                path.addEllipse(QRectF(p1, p2))
            elif self.annotation_data.annotation_type == AnnotationType.LINE:
                line_path = QPainterPath(p1)
                line_path.lineTo(p2)
                path.addPath(line_path)
                self.annotation_data.name = str(int(QVector2D(p2 - p1).length() * self.microns_per_pixel))
        elif self.annotation_data.annotation_type == AnnotationType.POLYGON:
            path.addPolygon(QPolygonF(self.annotation_data.points))
        self.shape_item.setPath(path)

    def update_text(self):
        if self.shape_item.path().length():
            self.prepareGeometryChange()
            # length = QVector2D(
            #     self.shape_item.boundingRect().topLeft() - self.shape_item.boundingRect().bottomRight()).length()
            # self.annotation_text.text.setText(str(length))
            self.annotation_text.prepareGeometryChange()
            self.annotation_text.text.setText(self.annotation_data.name)
            self.annotation_text.background.setRect(
                self.annotation_text.text.boundingRect() + create_annotation_text_margins())
            self.annotation_text.text.setPos(self.shape_item.boundingRect().center())
            self.annotation_text.background.setPos(self.shape_item.boundingRect().center())

    def update_style(self):
        pen = self.shape_item.pen()
        pen.setColor(self.annotation_data.pen_color)
        # print("isSelected:", self.isSelected())
        pen.setWidth(5 if self.isSelected() else 2)
        self.setCursor(Qt.ClosedHandCursor if self.isSelected() else Qt.ArrowCursor)
        pen.setCosmetic(True)
        self.shape_item.setPen(pen)

        brush = self.annotation_text.background.brush()
        brush.setColor(self.annotation_data.text_background_color)
        self.annotation_text.background.setBrush(brush)

    def set_last_point(self, p: QPointF):
        self.annotation_data.points[-1] = p
        self.update()

    def add_point(self, p: QPointF):
        self.annotation_data.points.append(p)
        self.update()

    def first_point(self) -> QPointF:
        return self.annotation_data.points[0]

    def itemChange(self, change: QGraphicsItem.GraphicsItemChange, value: typing.Any) -> typing.Any:
        if change == QGraphicsItem.ItemSelectedHasChanged:
            # print("shape_item", self.shape_item.shape().boundingRect().toRect())
            # print("mouseGrabberItem", self.scene().mouseGrabberItem())
            # print("is_selected", self.shape_item.isSelected(), self.isSelected())
            self.update_style()
        else:
            return super().itemChange(change, value)

    def boundingRect(self) -> QRectF:
        return self.shape_item.boundingRect()

    def shape(self) -> QPainterPath:
        text_background_shape = self.mapFromItem(self.annotation_text, self.annotation_text.shape())
        # print("shape_item", self.shape_item.shape().boundingRect().toRect())
        # print("background", text_background_shape.boundingRect().toRect())
        # path = self.shape_item.path() + text_background_shape
        path = text_background_shape
        shape_path = self.shape_item.shape()
        # shape_path = shape_path - shape_path.toReversed()
        # shape_path = shape_path - shape_path.translated(0.01,0)
        # path = shape_path + text_background_shape
        path = shape_path
        path = QPainterPathStroker().createStroke(path)
        return path + text_background_shape
