import typing
from typing import cast

from PyQt5.QtCore import Qt, pyqtProperty, pyqtSignal, QVariant, pyqtBoundSignal
from PyQt5.QtWidgets import QComboBox, QWidget, QStyledItemDelegate, QAbstractItemDelegate


# class DropdownCreatorBase(QItemEditorCreatorBase):
#
#     def __init__(self, items: typing.Iterable, *args, **kwargs):
#         super().__init__(*args, **kwargs)
#         self.items = items
#
#     def createWidget(self, parent: QWidget) -> QWidget:
#         return Dropdown(self.items, parent)

# T=TypeVar()

class Dropdown(QComboBox):
	selectedItemChanged = pyqtSignal(object)

	def __init__(self, items: typing.Iterable, selected_item_value, parent: typing.Optional[QWidget] = None,
				 selectedItemChanged=None,
				 label_func: typing.Callable[[typing.Any], str] = str,
				 value_func: typing.Callable[[typing.Any], str] = lambda x: x) -> None:
		super().__init__(parent)
		self.setEditable(False)
		self.value_to_item = {}
		self.label_func = label_func
		self.value_func = value_func
		self.items = items
		self.set_items(items)
		self.currentIndexChanged.connect(self.on_current_index_changed)
		if selectedItemChanged:
			self.selectedItemChanged.connect(selectedItemChanged)
		self.set_item_value(selected_item_value)

	def on_current_index_changed(self, i):
		selected_item = self.currentData(Qt.UserRole)
		if selected_item == QVariant():
			self.selectedItemChanged.emit(QVariant())
		else:
			selected_item_value = self.value_func(selected_item)
			self.selectedItemChanged.emit(selected_item_value)

	def set_items(self, items: typing.Iterable):
		self.clear()
		self.value_to_item.clear()
		for i, item in enumerate(items):
			text = self.label_func(item)
			value = self.value_func(item)
			self.value_to_item[value] = item
			self.insertItem(i, text, item)

	def get_item_value(self):
		item = self.currentData(Qt.UserRole)
		if item == QVariant():
			return QVariant()
		else:
			value = self.value_func(item)
			return QVariant(value)

	def set_item_value(self, value):
		item = self.value_to_item.get(value, None)
		if item:
			index = self.findData(item, Qt.UserRole)
		else:
			index = -1
		self.setCurrentIndex(index)

	itemProperty = pyqtProperty(QVariant, get_item_value, set_item_value, user=True)


def commit_close_after_dropdown_select(delegate: QStyledItemDelegate, dropdown: Dropdown) -> Dropdown:
	def on_selected_item_changed(item):
		delegate.commitData.emit(dropdown)
		delegate.closeEditor.emit(dropdown, QAbstractItemDelegate.NoHint)

	dropdown.selectedItemChanged.connect(on_selected_item_changed)
	cast(pyqtBoundSignal, dropdown.activated).connect(on_selected_item_changed)
	return dropdown
