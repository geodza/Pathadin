import typing

from PyQt5.QtCore import QPointF, QRectF, Qt
from PyQt5.QtGui import *
from PyQt5.QtWidgets import QGraphicsItemGroup, QGraphicsPathItem, QGraphicsItem

from slide_viewer.ui.common.common import join_odict_values
from slide_viewer.ui.dict_tree_view_model.standard_attr_key import StandardAttrKey
from slide_viewer.ui.slide.graphics.annotation.annotation_data import AnnotationData
from slide_viewer.ui.slide.graphics.annotation.annotation_text_item import AnnotationTextItem
from slide_viewer.ui.slide.graphics.annotation.annotation_type import AnnotationType
from slide_viewer.ui.slide.graphics.annotation.annotation_utls import create_annotation_text_margins, point_to_tuple


def calc_polygon_area(polygon: QPolygonF):
    area = 0
    for i in range(polygon.size()):
        pi, pj = polygon[i], polygon[i - 1]
        area += (pj.x() + pi.x()) * (pj.y() - pi.y())
    return abs(area) / 2


def calc_length(p1: QPointF, p2: QPointF):
    return QVector2D(p2 - p1).length()


class AnnotationPathItem(QGraphicsItemGroup):
    def __init__(self, annotation_data: AnnotationData = None, microns_per_pixel=1, scale=1):
        super().__init__()
        if len(annotation_data.display_attr_keys) < 2:
            if annotation_data.annotation_type == AnnotationType.LINE:
                annotation_data.display_attr_keys = [StandardAttrKey.name.name, StandardAttrKey.length.name]
            else:
                annotation_data.display_attr_keys = [StandardAttrKey.name.name, StandardAttrKey.area.name]

        self.microns_per_pixel = microns_per_pixel
        self.scale = scale

        self.shape_item = QGraphicsPathItem(self)
        self.shape_item.setAcceptedMouseButtons(Qt.NoButton)
        self.annotation_text = AnnotationTextItem(self)
        self.setFlag(QGraphicsItem.ItemSendsGeometryChanges)
        self.setFlag(QGraphicsItem.ItemSendsScenePositionChanges)

        self.annotation_data: AnnotationData = annotation_data
        self.is_in_progress = False
        self.update()

    def update(self, rect: QRectF = QRectF()) -> None:
        self.setFlag(QGraphicsItem.ItemIsMovable, not self.is_in_progress)
        self.setFlag(QGraphicsItem.ItemIsSelectable, not self.is_in_progress)
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
                # self.annotation_data.name = str(int(calc_length(p1, p2) * self.microns_per_pixel))
        elif self.annotation_data.annotation_type == AnnotationType.POLYGON:
            path.addPolygon(QPolygonF(self.annotation_data.points))

        if self.annotation_data.annotation_type == AnnotationType.LINE:
            p1 = self.annotation_data.points[0]
            p2 = self.annotation_data.points[-1]
            self.annotation_data.length = str(int(calc_length(p1, p2) * self.microns_per_pixel))
        else:
            area = calc_polygon_area(path.toFillPolygon()) * self.microns_per_pixel ** 2
            self.annotation_data.area = str(int(area))

        self.shape_item.setPath(path)
        self.setPos(self.annotation_data.points[0])
        self.shape_item.setPos(-self.pos())
        self.annotation_text.setPos(-self.pos())

    def update_text(self):
        if self.shape_item.path().length():
            self.prepareGeometryChange()
            self.annotation_text.setVisible(not self.annotation_data.text_hidden)
            self.annotation_text.prepareGeometryChange()
            display_str = join_odict_values(self.annotation_data.odict, self.annotation_data.display_attr_keys)
            self.annotation_text.text.setText(display_str)
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
            self.update_style()
        elif change == QGraphicsItem.ItemPositionChange:
            return super().itemChange(change, value)
        elif change == QGraphicsItem.ItemPositionHasChanged:
            shift = self.pos() - self.annotation_data.points[0]
            self.annotation_data.points = [p + shift for p in self.annotation_data.points]
            self.update()
            return
        else:
            return super().itemChange(change, value)

    def boundingRect(self) -> QRectF:
        # return self.shape_item.boundingRect()
        return self.shape().boundingRect()

    def shape(self) -> QPainterPath:
        shape_path = self.shape_item.shape()
        stroker = QPainterPathStroker()
        stroker.setWidth(20 / self.scale)
        path = stroker.createStroke(shape_path)
        return path.translated(self.shape_item.pos().x(), self.shape_item.pos().y())
