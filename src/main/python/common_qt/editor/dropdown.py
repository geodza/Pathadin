import typing
from typing import cast

from PyQt5.QtCore import Qt, pyqtProperty, pyqtSignal, QObject, QVariant, pyqtBoundSignal
from PyQt5.QtWidgets import QComboBox, QWidget, QItemEditorCreatorBase, QStyledItemDelegate


# class DropdownCreatorBase(QItemEditorCreatorBase):
#
#     def __init__(self, items: typing.Iterable, *args, **kwargs):
#         super().__init__(*args, **kwargs)
#         self.items = items
#
#     def createWidget(self, parent: QWidget) -> QWidget:
#         return Dropdown(self.items, parent)


class Dropdown(QComboBox):
    selectedItemChanged = pyqtSignal(object)

    def __init__(self, items: typing.Iterable, selected_item, parent: typing.Optional[QWidget] = None,
                 selectedItemChanged=None) -> None:
        super().__init__(parent)
        self.setEditable(False)
        self.items = items
        self.set_items(items)
        self.currentIndexChanged.connect(self.on_current_index_changed)
        if selectedItemChanged:
            self.selectedItemChanged.connect(selectedItemChanged)
        self.set_item(selected_item)

    def on_current_index_changed(self, i):
        selected_item = self.currentData(Qt.UserRole)
        self.selectedItemChanged.emit(selected_item)

    def set_items(self, items: typing.Iterable):
        self.clear()
        for i, item in enumerate(items):
            text = str(item)
            self.insertItem(i, text, item)

    def get_item(self):
        item = self.currentData(Qt.UserRole)
        return QVariant(item)

    def set_item(self, item):
        index = self.findData(item, Qt.UserRole)
        self.setCurrentIndex(index)

    itemProperty = pyqtProperty(QVariant, get_item, set_item, user=True)


def commit_close_after_dropdown_select(delegate: QStyledItemDelegate, dropdown: Dropdown) -> Dropdown:
	def on_selected_item_changed(item):
		delegate.commitData.emit(dropdown)
		delegate.closeEditor.emit(dropdown)

	dropdown.selectedItemChanged.connect(on_selected_item_changed)
	cast(pyqtBoundSignal, dropdown.activated).connect(on_selected_item_changed)
	return dropdown