import typing

from PyQt5.QtCore import QSize
from PyQt5.QtWidgets import QWidget, QStyleOptionViewItem, QMenu

from common_qt.action.my_menu import create_menu
from common_qt.editor.file_path_editor import FilePathEditor
from common_qt.mvc.model.delegate.item_model_delegate import AbstractItemModelDelegate
from common_qt.mvc.view.delegate.abstract_item_view_context_menu_delegate import AbstractItemViewContextMenuDelegate
from common_qt.mvc.view.delegate.abstract_item_view_delegate import AbstractItemViewDelegate
from deepable.core import first_last_keys, deep_keys
from deepable_qt.model.deepable_model_index import DeepableQModelIndex
from deepable_qt.model.deepable_tree_model import DeepableTreeModel
from deepable_qt.model.standard_deepable_tree_model_delegate import StandardDeepableTreeModelDelegate
from deepable_qt.view.deepable_tree_view import DeepableTreeView
from filter_template.filter_template_item_model_delegate_factory import FilterTemplateItemModelDelegateFactory, \
	FilterTemplateItemModelDelegate
from filter_template.filter_template_item_view_context_menu_delegate import FilterTemplateItemViewContextMenuDelegate
from filter_template.filter_template_item_view_context_menu_delegate_factory import \
	FilterTemplateItemViewContextMenuDelegateFactory
from filter_template.filter_template_item_view_delegate import ImmutableFilterTemplateTreeViewDelegate
from filter_template.filter_template_item_viewl_delegate_factory import FilterTemplateItemViewDelegateFactory
from filter.common.filter_data import FilterData

from filter.keras.keras_model_filter_model import KerasModelParams, KerasModelFilterData, KerasModelParams_

I = DeepableQModelIndex
M = DeepableTreeModel
V = DeepableTreeView
F = KerasModelFilterData

class KerasModelFilterContextMenuDelegateFactory(FilterTemplateItemViewContextMenuDelegateFactory):

	def _create_delegate(self, index: I, view: V, filter_data) -> typing.Optional[
		AbstractItemViewContextMenuDelegate[I, V]]:
		if not index.isValid():
			return KerasModelFilterContextMenuDelegate(view)
		elif isinstance(filter_data, KerasModelFilterData):
			return KerasModelFilterContextMenuDelegate(view)
		else:
			return None


class KerasModelFilterContextMenuDelegate(FilterTemplateItemViewContextMenuDelegate):

	def create_menu(self, index: I) -> typing.Optional[QMenu]:
		actions = []
		# Index may be invalid => no model for invalid index. So take model from view.
		model = self.view.model()
		if not index.isValid():
			add_action = self.create_add_action("Add keras model filter", "keras_model_filter_", lambda k: KerasModelFilterData(k, k))
			actions.append(add_action)
			menu = create_menu("Keras model", actions)
			return menu
		else:
			return None

class KerasModelFilterModelDelegateFactory(FilterTemplateItemModelDelegateFactory):

	def _create(self, index: I, filter_data: F) -> typing.Optional[AbstractItemModelDelegate[I]]:
		if isinstance(filter_data, KerasModelFilterData):
			return KerasModelFilterModelDelegate()


class KerasModelFilterModelDelegate(FilterTemplateItemModelDelegate):

	def _is_index_readonly(self, index: I) -> bool:
		model = index.model()
		key, value = model.key(index), model.value(index)
		filter_key, last_key = first_last_keys(key)
		filter_data: FilterData = model[filter_key]
		# print(f"_is_index_readonly {last_key}")
		keys = deep_keys(KerasModelParams)
		if index.column() == 1 and last_key in keys:
			return False
		return super()._is_index_readonly(index)


class KerasModelFilterViewDelegateFactory(FilterTemplateItemViewDelegateFactory):

	def _create(self, index: I, filter_data: F) -> typing.Optional[AbstractItemViewDelegate[I, M, V]]:
		if isinstance(filter_data, KerasModelFilterData):
			return KerasModelFilterViewDelegate()


class KerasModelFilterViewDelegate(ImmutableFilterTemplateTreeViewDelegate):

	def filter_data_type(self, filter_data_dict: dict) -> type:
		return KerasModelFilterData

	def _createEditor(self, parent: QWidget, option: QStyleOptionViewItem, index: I, key: str,
					  filter_data: F) -> QWidget:
		model = index.model()
		filter_key, last_key = first_last_keys(key)
		value = model.value(index)
		# keys = deep_keys(KerasModelParams)
		if last_key == KerasModelParams_.model_path:
			file_path_editor = FilePathEditor(parent, value)
			return file_path_editor

		return super()._createEditor(parent, option, index, key, filter_data)

	def _sizeHint(self, option: QStyleOptionViewItem, index: I, key: str) -> QSize:
		return super()._sizeHint(option, index, key)
