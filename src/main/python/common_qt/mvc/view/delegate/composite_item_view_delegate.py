import typing

from PyQt5 import QtCore, QtGui
from PyQt5.QtCore import QModelIndex, QAbstractItemModel
from PyQt5.QtWidgets import QWidget, QStyleOptionViewItem, QAbstractItemView, \
	QMenu
from dataclasses import dataclass, field

from common_qt.mvc.view.delegate.abstract_item_view_delegate import AbstractItemViewDelegate
from common_qt.mvc.view.delegate.factory.abstract_item_view_delegate_factory import AbstractItemViewDelegateFactory

T = typing.TypeVar('T', bound=QModelIndex)
M = typing.TypeVar('M', bound=QAbstractItemModel)
V = typing.TypeVar('V', bound=QAbstractItemView)


@dataclass
class CompositeItemViewDelegate(AbstractItemViewDelegate, typing.Generic[T, M, V]):
	factories: typing.List[AbstractItemViewDelegateFactory[T, M, V]] = field(default_factory=list)

	def __post_init__(self):
		super().__init__()

	def find_delegate(self, index: T) -> AbstractItemViewDelegate:
		for f in self.factories:
			d = f.create(index)
			if d is not None:
				# try:
				d.closeEditor.connect(self.closeEditor)
				d.commitData.connect(self.commitData)
				d.sizeHintChanged.connect(self.sizeHintChanged)
				# except TypeError:
				# 	pass
				return d
		raise ValueError(f"CompositeItemViewDelegate. No appropriate delegate found in {self.factories}")

	def editorEvent(self, event: QtCore.QEvent, model: M, option: QStyleOptionViewItem,
					index: T) -> bool:
		return self.find_delegate(index).editorEvent(event, model, option, index)

	def initStyleOption(self, option: QStyleOptionViewItem, index: T) -> None:
		self.find_delegate(index).initStyleOption(option, index)

	def updateEditorGeometry(self, editor: QWidget, option: QStyleOptionViewItem, index: T) -> None:
		self.find_delegate(index).updateEditorGeometry(editor, option, index)

	def setModelData(self, editor: QWidget, model: M, index: T) -> None:
		self.find_delegate(index).setModelData(editor, model, index)

	def setEditorData(self, editor: QWidget, index: T) -> None:
		self.find_delegate(index).setEditorData(editor, index)

	def createEditor(self, parent: QWidget, option: QStyleOptionViewItem, index: T) -> QWidget:
		return self.find_delegate(index).createEditor(parent, option, index)

	def sizeHint(self, option: QStyleOptionViewItem, index: T) -> QtCore.QSize:
		return self.find_delegate(index).sizeHint(option, index)

	def paint(self, painter: QtGui.QPainter, option: QStyleOptionViewItem, index: T) -> None:
		self.find_delegate(index).paint(painter, option, index)

	def helpEvent(self, event: QtGui.QHelpEvent, view: V, option: QStyleOptionViewItem,
				  index: T) -> bool:
		return self.find_delegate(index).helpEvent(event, view, option, index)

	def destroyEditor(self, editor: QWidget, index: T) -> None:
		self.find_delegate(index).destroyEditor(editor, index)