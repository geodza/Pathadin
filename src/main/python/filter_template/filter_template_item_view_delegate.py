from abc import abstractmethod, ABC
from typing import Type, TypeVar

from PyQt5.QtCore import QSize
from PyQt5.QtWidgets import QWidget, QStyleOptionViewItem
from dacite import from_dict

from common_qt.editor.dropdown import Dropdown
from common_qt.editor.file_path_editor import FilePathEditor
from common_qt.editor.list_editor import SelectListEditor
from common_qt.mvc.view.delegate.abstract_item_view_delegate import AbstractItemViewDelegate
from deepable.convert import deep_to_dict
from deepable.core import deep_set
from deepable_qt.model.deepable_model_index import DeepableQModelIndex
from deepable_qt.model.deepable_tree_model import DeepableTreeModel
from deepable_qt.view.deepable_tree_view import DeepableTreeView
from filter.common.filter_model import FilterData

I = DeepableQModelIndex
M = DeepableTreeModel
V = DeepableTreeView

T = TypeVar('T')


class ImmutableFilterTemplateTreeViewDelegate(AbstractItemViewDelegate[I, M, V], ABC):

	@abstractmethod
	def filter_data_type(self, filter_data_dict: dict) -> type:
		pass

	def setModelData(self, editor: QWidget, model: M, index: I) -> None:
		key, value = model.key(index), model.value(index)
		filter_key, *attr_path = key.split('.')
		filter_data = model[filter_key]
		value = editor.metaObject().userProperty().read(editor)
		filter_data_dict = deep_to_dict(filter_data)
		deep_set(filter_data_dict, '.'.join(attr_path), value)
		new_filter_data = self._dict_to_data(filter_data_dict)
		model[filter_key] = new_filter_data

	def _dict_to_data(self, filter_data_dict: dict):
		type_=self.filter_data_type(filter_data_dict)
		return from_dict(type_, filter_data_dict)

	# return deep_from_dict(filter_data_dict, self.filter_data_type(filter_data_dict))

	# def setEditorData(self, editor: QWidget, index: T) -> None:
	# 	super().setEditorData(editor, index)

	def createEditor(self, parent: QWidget, option: QStyleOptionViewItem, index: I) -> QWidget:
		model = index.model()
		key, value = model.key(index), model.value(index)
		filter_key = key.split(".")[0]
		filter_data: FilterData = model[filter_key]
		return self._createEditor(parent, option, index, key, filter_data)

	def _createEditor(self, parent: QWidget, option: QStyleOptionViewItem, index: I, key: str,
					  filter_data) -> QWidget:
		return super().createEditor(parent, option, index)

	def sizeHint(self, option: QStyleOptionViewItem, index: I) -> QSize:
		model = index.model()
		key = model.key(index)
		return self._sizeHint(option, index, key)

	def _sizeHint(self, option: QStyleOptionViewItem, index: I, key: str) -> QSize:
		return super().sizeHint(option, index)

	def updateEditorGeometry(self, editor: QWidget, option: QStyleOptionViewItem, index: I) -> None:
		if isinstance(editor, Dropdown):
			super().updateEditorGeometry(editor, option, index)
			editor.showPopup()
		elif isinstance(editor, FilePathEditor):
			super().updateEditorGeometry(editor, option, index)
			editor.show_dialog()
		if isinstance(editor, SelectListEditor):
			editor.adjustSize()
			super().updateEditorGeometry(editor, option, index)
		else:
			super().updateEditorGeometry(editor, option, index)
