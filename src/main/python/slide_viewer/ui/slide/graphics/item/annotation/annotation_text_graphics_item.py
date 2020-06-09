from typing import Optional

from PyQt5.QtCore import Qt, QMarginsF
from PyQt5.QtGui import QColor
from PyQt5.QtWidgets import QGraphicsItem, QGraphicsRectItem, QGraphicsItemGroup, \
	QGraphicsTextItem, QApplication
from dataclasses import dataclass

from common.log_utils import log


@dataclass
class AnnotationTextGraphicsItem(QGraphicsItemGroup):
	_text: Optional[str] = None
	_background_color: QColor = QColor('green')

	def __post_init__(self):
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
		self.sync()

	def set_background_color(self, _background_color: QColor):
		if self._background_color != _background_color:
			self._background_color = _background_color
			self.sync_background_color()

	def set_text(self, text: Optional[str]):
		if self._text != text:
			self._text = text
			self.sync_text()

	def sync(self):
		self.sync_background_color()
		self.sync_text()
		self.update()

	def sync_background_color(self):
		background_color = self._background_color
		brush = self.background.brush()
		brush.setStyle(Qt.SolidPattern)
		brush.setColor(background_color)
		self.background.setBrush(brush)
		self.background.update()

	def sync_text(self):
		text = self._text
		self.prepareGeometryChange()
		self.text_item.setHtml(text)
		self.background.setRect(self.text_item.boundingRect() + QMarginsF(4, 4, 4, 4))
		self.text_item.update()
		self.background.update()


def create_annotation_text_font():
	f = QApplication.font()
	f.setPointSize(int(f.pointSize() * 1.2))
	return f
