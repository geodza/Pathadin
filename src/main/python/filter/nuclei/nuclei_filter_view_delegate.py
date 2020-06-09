import typing

from PyQt5.QtCore import QSize
from PyQt5.QtWidgets import QWidget, QStyleOptionViewItem, QMenu

from common_qt.action.my_menu import create_menu
from common_qt.mvc.model.delegate.item_model_delegate import AbstractItemModelDelegate
from common_qt.mvc.view.delegate.abstract_item_view_context_menu_delegate import AbstractItemViewContextMenuDelegate
from common_qt.mvc.view.delegate.abstract_item_view_delegate import AbstractItemViewDelegate
from deepable.core import first_last_keys, deep_keys
from deepable_qt.model.deepable_model_index import DeepableQModelIndex
from deepable_qt.model.deepable_tree_model import DeepableTreeModel
from deepable_qt.view.deepable_tree_view import DeepableTreeView
from filter.nuclei.nuclei_filter_model import NucleiFilterData, NucleiParams
from filter_template.filter_template_item_model_delegate_factory import FilterTemplateItemModelDelegateFactory, \
	FilterTemplateItemModelDelegate
from filter_template.filter_template_item_view_context_menu_delegate import FilterTemplateItemViewContextMenuDelegate
from filter_template.filter_template_item_view_context_menu_delegate_factory import \
	FilterTemplateItemViewContextMenuDelegateFactory
from filter_template.filter_template_item_view_delegate import ImmutableFilterTemplateTreeViewDelegate
from filter_template.filter_template_item_viewl_delegate_factory import FilterTemplateItemViewDelegateFactory

I = DeepableQModelIndex
M = DeepableTreeModel
V = DeepableTreeView
F = NucleiFilterData


class NucleiFilterContextMenuDelegateFactory(FilterTemplateItemViewContextMenuDelegateFactory):

	def _create_delegate(self, index: I, view: V, filter_data) -> typing.Optional[
		AbstractItemViewContextMenuDelegate[I, V]]:
		if not index.isValid():
			return NucleiFilterContextMenuDelegate(view)
		elif isinstance(filter_data, NucleiFilterData):
			return NucleiFilterContextMenuDelegate(view)
		else:
			return None


class NucleiFilterContextMenuDelegate(FilterTemplateItemViewContextMenuDelegate):

	def create_menu(self, index: I) -> typing.Optional[QMenu]:
		actions = []
		# Index may be invalid => no model for invalid index. So take model from view.
		model = self.view.model()
		if not index.isValid():
			add_action = self.create_add_action("Add nuclei filter", "nuclei_filter_", lambda k: NucleiFilterData(k, k))
			actions.append(add_action)
			menu = create_menu("Nuclei", actions)
			return menu
		else:
			return None


class NucleiFilterModelDelegateFactory(FilterTemplateItemModelDelegateFactory):

	def _create(self, index: I, filter_data: F) -> typing.Optional[AbstractItemModelDelegate[I]]:
		if isinstance(filter_data, NucleiFilterData):
			return NucleiFilterModelDelegate()


class NucleiFilterModelDelegate(FilterTemplateItemModelDelegate):

	def _is_index_readonly(self, index: I) -> bool:
		model = index.model()
		key, value = model.key(index), model.value(index)
		filter_key, last_key = first_last_keys(key)
		keys = deep_keys(NucleiParams)
		if index.column() == 1 and last_key in keys:
			return False
		return super()._is_index_readonly(index)


class NucleiFilterViewDelegateFactory(FilterTemplateItemViewDelegateFactory):

	def _create(self, index: I, filter_data) -> typing.Optional[AbstractItemViewDelegate[I, M, V]]:
		if isinstance(filter_data, F):
			return NucleiFilterViewDelegate()


class NucleiFilterViewDelegate(ImmutableFilterTemplateTreeViewDelegate):

	def filter_data_type(self, filter_data_dict: dict) -> type:
		return NucleiFilterData

	def _createEditor(self, parent: QWidget, option: QStyleOptionViewItem, index: I, key: str,
					  filter_data: F) -> QWidget:
		model = index.model()
		filter_key, last_key = first_last_keys(key)
		value = model.value(index)
		keys = deep_keys(NucleiParams)
		if last_key in keys:
			return super()._createEditor(parent, option, index, key, filter_data)
		return super()._createEditor(parent, option, index, key, filter_data)

	def _sizeHint(self, option: QStyleOptionViewItem, index: I, key: str) -> QSize:
		return super()._sizeHint(option, index, key)
