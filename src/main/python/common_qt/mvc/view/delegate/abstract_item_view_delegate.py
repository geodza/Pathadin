import typing
from functools import wraps

from PyQt5 import QtCore, QtGui
from PyQt5.QtCore import QModelIndex, QAbstractItemModel, pyqtSignal, QObject
from PyQt5.QtWidgets import QStyledItemDelegate, QWidget, QStyleOptionViewItem, \
	QAbstractItemView, QAbstractItemDelegate

T = typing.TypeVar('T', bound=QModelIndex)
M = typing.TypeVar('M', bound=QAbstractItemModel)
V = typing.TypeVar('V', bound=QAbstractItemView)


def item_view_delegate_wrapper(method):
	@wraps(method)
	def _impl(self, *method_args, **method_kwargs):
		item_view_delegate: QStyledItemDelegate = self._itd
		delegate_method = getattr(item_view_delegate, method.__name__)
		method_output = delegate_method(*method_args, **method_kwargs)
		return method_output

	return _impl


# class QGenericMeta(type(QObject), type(typing.Generic)):
# class QGenericMeta(type(QObject), typing.GenericMeta):
# 	pass

# class QGenericMeta(typing.GenericMeta,type(QObject)):
# 	pass

class AbstractItemViewDelegateSignals(QObject):
	closeEditor = pyqtSignal([QWidget, QAbstractItemDelegate.EndEditHint], [QWidget])
	commitData = pyqtSignal(QWidget)
	sizeHintChanged = pyqtSignal(QModelIndex)


class AbstractItemViewDelegate(typing.Generic[T, M, V]):

	def __init__(self):
		self.signals = AbstractItemViewDelegateSignals()
		self._itd = QStyledItemDelegate()

	@property
	def closeEditor(self):
		return self.signals.closeEditor

	@property
	def commitData(self):
		return self.signals.commitData

	@property
	def sizeHintChanged(self):
		return self.signals.sizeHintChanged

	@item_view_delegate_wrapper
	def editorEvent(self, event: QtCore.QEvent, model: M, option: QStyleOptionViewItem,
					index: T) -> bool:
		pass

	# def eventFilter(self, object: QtCore.QObject, event: QtCore.QEvent) -> bool:
	# 	return super().eventFilter(object, event)

	@item_view_delegate_wrapper
	def initStyleOption(self, option: QStyleOptionViewItem, index: T) -> None:
		pass

	# def displayText(self, value: typing.Any, locale: QtCore.QLocale) -> str:
	# 	return super().displayText(value, locale)

	# def setItemEditorFactory(self, factory: QItemEditorFactory) -> None:
	# 	super().setItemEditorFactory(factory)

	# def itemEditorFactory(self) -> QItemEditorFactory:
	# 	return super().itemEditorFactory()

	@item_view_delegate_wrapper
	def updateEditorGeometry(self, editor: QWidget, option: QStyleOptionViewItem, index: T) -> None:
		pass

	@item_view_delegate_wrapper
	def setModelData(self, editor: QWidget, model: M, index: T) -> None:
		pass

	@item_view_delegate_wrapper
	def setEditorData(self, editor: QWidget, index: T) -> None:
		pass

	@item_view_delegate_wrapper
	def createEditor(self, parent: QWidget, option: QStyleOptionViewItem, index: T) -> QWidget:
		pass

	@item_view_delegate_wrapper
	def sizeHint(self, option: QStyleOptionViewItem, index: T) -> QtCore.QSize:
		pass

	@item_view_delegate_wrapper
	def paint(self, painter: QtGui.QPainter, option: QStyleOptionViewItem, index: T) -> None:
		pass

	@item_view_delegate_wrapper
	def helpEvent(self, event: QtGui.QHelpEvent, view: V, option: QStyleOptionViewItem,
				  index: T) -> bool:
		# TODO index here can be None !? Where else it can be None?
		pass

	@item_view_delegate_wrapper
	def destroyEditor(self, editor: QWidget, index: T) -> None:
		pass
