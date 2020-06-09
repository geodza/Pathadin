import typing
from typing import List

from PyQt5 import QtGui
from PyQt5.QtCore import QRectF, Qt, QPoint, QMarginsF
from PyQt5.QtGui import *
from PyQt5.QtWidgets import QGraphicsItemGroup, QGraphicsPathItem, QGraphicsItem, QStyleOptionGraphicsItem, QWidget
from dataclasses import dataclass

from annotation.annotation_type import AnnotationType
from common.log_utils import log
from common_qt.metrics import are_points_distinguishable
from slide_viewer.ui.slide.widget.interface.scale_view_provider import ScaleProvider


def build_painter_path(annotation_type: AnnotationType, points: List[QPoint]) -> QPainterPath:
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

@dataclass(frozen=True)
class AnnotationFigurePathGraphicsItemDto:
	annotation_type: AnnotationType
	points: List[QPoint]

# color: QColor = QColor('green')


@dataclass
class AnnotationFigureGraphicsItem(QGraphicsItemGroup):
	scale_provider: ScaleProvider
	_item_dto: AnnotationFigurePathGraphicsItemDto
	_color: QColor = QColor('green')

	def __post_init__(self):
		QGraphicsItemGroup.__init__(self)
		self.shape_item = QGraphicsPathItem(self)
		self.shape_item.setAcceptHoverEvents(False)
		self.shape_item.setAcceptedMouseButtons(Qt.NoButton)
		self.setFlag(QGraphicsItem.ItemIsSelectable)
		self.setFlag(QGraphicsItem.ItemSendsGeometryChanges)
		self.sync()

	def set_color(self, color: QColor):
		if self._color != color:
			self._color = color
			self.sync_color()

	def set_item_data(self, dto: AnnotationFigurePathGraphicsItemDto):
		if self._item_dto != dto:
			self._item_dto = dto
			self.sync_item_dto()

	def sync(self):
		self.sync_color()
		self.sync_item_dto()
		self.update()

	def sync_color(self):
		color = self._color
		pen = self.shape_item.pen()
		pen.setColor(color)
		self.shape_item.setPen(pen)
		self.shape_item.update()

	def sync_item_dto(self):
		annotation_type, points = self._item_dto.annotation_type, self._item_dto.points
		self.prepareGeometryChange()
		path = build_painter_path(annotation_type, points)
		self.shape_item.setPath(path)
		self.shape_item.update()

	def update(self, rect: QRectF = QRectF()) -> None:
		pen = self.shape_item.pen()
		pen.setStyle(Qt.DotLine if self.isSelected() else Qt.SolidLine)
		pen.setCosmetic(True)
		new_pen_width = 5 if self.isSelected() else 3
		if new_pen_width != pen.width():
			self.prepareGeometryChange()
			pen.setWidth(new_pen_width)
		self.shape_item.setPen(pen)
		super().update(rect)

	# def itemChange(self, change: QGraphicsItem.GraphicsItemChange, value: typing.Any) -> typing.Any:
	# 	if change == QGraphicsItem.ItemSelectedHasChanged:
	# 		pen = self.shape_item.pen()
	# 		pen.setStyle(Qt.DotLine if value else Qt.SolidLine)
	# 		new_pen_width = 10 if value else 6
	# 		if new_pen_width != pen.width():
	# 			self.prepareGeometryChange()
	# 			pen.setWidth(new_pen_width)
	# 		self.shape_item.setPen(pen)
	# 		self.update()
	# 		return super().itemChange(change, value)
	# 	return super().itemChange(change, value)

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
