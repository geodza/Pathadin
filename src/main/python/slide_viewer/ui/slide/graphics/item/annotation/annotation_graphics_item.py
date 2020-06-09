from typing import Any, Optional

from PyQt5.QtCore import QPointF, QRectF, pyqtSignal, QObject, QPoint
from PyQt5.QtGui import *
from PyQt5.QtGui import QColor
from PyQt5.QtWidgets import QGraphicsItemGroup, QGraphicsItem
from dataclasses import dataclass, field

from common_qt.metrics import are_points_distinguishable
from common_qt.util.debounce import qt_debounce
from slide_viewer.ui.slide.graphics.item.annotation.annotation_figure_graphics_item import AnnotationFigureGraphicsItem, \
	AnnotationFigurePathGraphicsItemDto
from slide_viewer.ui.slide.graphics.item.annotation.annotation_text_graphics_item import AnnotationTextGraphicsItem
from slide_viewer.ui.slide.widget.interface.scale_view_provider import ScaleProvider


@dataclass
class AnnotationFigureGraphicsItemDto:
	path_item_dto: AnnotationFigurePathGraphicsItemDto
	color: QColor


@dataclass
class AnnotationTextGraphicsItemDto:
	text: Optional[str]
	background_color: QColor = QColor('green')


@dataclass
class AnnotationGraphicsItemDto:
	id: str
	pos: QPoint
	figure_item_dto: AnnotationFigureGraphicsItemDto
	text_item_dto: AnnotationTextGraphicsItemDto
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
	_pos: QPoint
	_figure_item_dto: AnnotationFigureGraphicsItemDto
	_text_item_dto: AnnotationTextGraphicsItemDto
	_figure_hidden: bool
	_text_hidden: bool
	_is_in_progress: bool
	signals: AnnotationGraphicsItemSignals = field(default_factory=AnnotationGraphicsItemSignals)

	@property
	def pos_(self):
		return self._pos

	@property
	def figure_item_dto(self):
		return self._figure_item_dto

	@property
	def text_item_dto(self):
		return self._text_item_dto

	@property
	def figure_hidden(self):
		return self._figure_hidden

	@property
	def text_hidden(self):
		return self._text_hidden

	@property
	def is_in_progress(self):
		return self._is_in_progress

	def __post_init__(self):
		QGraphicsItemGroup.__init__(self)
		self.figure = AnnotationFigureGraphicsItem(self.scale_provider, self._figure_item_dto.path_item_dto,
												   self._figure_item_dto.color)
		self.figure.setParentItem(self)
		self.text = AnnotationTextGraphicsItem(self._text_item_dto.text, self._text_item_dto.background_color)
		self.text.setParentItem(self)
		self.setFlag(QGraphicsItem.ItemSendsGeometryChanges)
		self.setFlag(QGraphicsItem.ItemSendsScenePositionChanges)
		self.sync()

	def set_pos(self, _pos: QPoint):
		if self._pos != _pos:
			self._pos = _pos
			self.sync_pos()

	def set_figure_item_dto(self, dto: AnnotationFigureGraphicsItemDto):
		if self._figure_item_dto != dto:
			self._figure_item_dto = dto
			self.sync_figure_item_dto()

	def set_text_item_dto(self, dto: AnnotationTextGraphicsItemDto):
		if self._text_item_dto != dto:
			self._text_item_dto = dto
			self.sync_text_item_dto()

	def set_figure_hidden(self, figure_hidden: bool):
		if self._figure_hidden != figure_hidden:
			self._figure_hidden = figure_hidden
			self.sync_figure_hidden()

	def set_text_hidden(self, text_hidden: bool):
		if self._text_hidden != text_hidden:
			self._text_hidden = text_hidden
			self.sync_text_hidden()

	def set_is_in_progress(self, is_in_progress: bool):
		if self._is_in_progress != is_in_progress:
			self._is_in_progress = is_in_progress
			self.sync_is_in_progress()

	def sync_pos(self):
		_pos = self._pos
		if _pos != self.pos():
			self.prepareGeometryChange()
			self.setPos(_pos)
			self.update()

	def sync_figure_item_dto(self):
		_figure_item_dto = self._figure_item_dto
		self.figure.set_color(_figure_item_dto.color)
		self.figure.set_item_data(_figure_item_dto.path_item_dto)
		self.figure.update()
		self.text.setPos(self.figure.boundingRect().center())
		self.text.update()

	def sync_text_item_dto(self):
		_text_item_dto = self._text_item_dto
		self.text.set_text(_text_item_dto.text)
		self.text.set_background_color(_text_item_dto.background_color)
		self.text.update()

	def sync_figure_hidden(self):
		self.figure.setVisible(not self._figure_hidden)
		self.figure.update()

	def sync_text_hidden(self):
		self.text.setVisible(not self._text_hidden)
		self.text.update()

	def sync_is_in_progress(self):
		self.setFlag(QGraphicsItem.ItemIsMovable, not self._is_in_progress)
		self.setFlag(QGraphicsItem.ItemIsSelectable, not self._is_in_progress)
		self.update()

	def sync(self):
		self.sync_pos()
		self.sync_figure_item_dto()
		self.sync_figure_hidden()
		self.sync_text_item_dto()
		self.sync_text_hidden()
		self.sync_is_in_progress()

	def update(self, rect: QRectF = QRectF()) -> None:
		# self.setFlag(QGraphicsItem.ItemIsMovable, not self.is_in_progress)
		# self.setFlag(QGraphicsItem.ItemIsSelectable, not self.is_in_progress)
		# QGraphicsItemGroup does not call update for children
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
			self.set_pos(value)
			self.emit_pos_changed_debounced_hack(value)
			# self.signals.posChanged.emit(self.id, value)
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

	@qt_debounce(0.2)
	def emit_pos_changed_debounced_hack(self, value):
		# TODO We need to debounce it in subscribers (like throttle, distinctUntilChanged in rxjs).
		# If this event will be debounced somewhere upper we will need to debounce it for each annotation_id separately!.
		# Will need to keep observable for each possible annotation_id? Another option is to use buffer/window (each 0.1 seconds) and get latest emitted (annotation_id, pos) tuples.
		self.signals.posChanged.emit(self.id, value)

	def boundingRect(self) -> QRectF:
		return self.figure.boundingRect()

	def shape(self) -> QPainterPath:
		return self.figure.shape()

	def is_distinguishable_from_point(self):
		return are_points_distinguishable(self._figure_item_dto.path_item_dto.points)
