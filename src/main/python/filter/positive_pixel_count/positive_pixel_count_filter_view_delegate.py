import typing

from PyQt5.QtCore import QModelIndex, Qt, QSize
from PyQt5.QtWidgets import QWidget, QStyleOptionViewItem

from common_qt.mvc.model.delegate.item_model_delegate import AbstractItemModelDelegate
from common_qt.mvc.view.delegate.item_view_delegate import AbstractItemViewDelegate
from deepable.core import deep_set, first_last_keys, deep_keys
from deepable_qt.model.deepable_model_index import DeepableQModelIndex
from deepable_qt.model.deepable_tree_model import DeepableTreeModel
from deepable_qt.model.standard_deepable_tree_model_delegate import StandardDeepableTreeModelDelegate
from deepable_qt.view.deepable_tree_view import DeepableTreeView
from filter_template.filter_template_item_model_delegate_factory import FilterTemplateItemModelDelegateFactory
from filter_template.filter_template_item_view_delegate import ImmutableFilterTemplateTreeViewDelegate
from filter_template.filter_template_item_viewl_delegate_factory import FilterTemplateItemViewDelegateFactory
from img.filter.nuclei import NucleiParams
from img.filter.positive_pixel_count import PositivePixelCountFilterData

T = DeepableQModelIndex
M = DeepableTreeModel
V = DeepableTreeView
F = PositivePixelCountFilterData


class PositivePixelCountFilterModelDelegateFactory(FilterTemplateItemModelDelegateFactory):

	def _create(self, index: T, filter_data: F) -> typing.Optional[AbstractItemModelDelegate[T]]:
		if isinstance(filter_data, PositivePixelCountFilterData):
			return PositivePixelCountFilterModelDelegate()


class PositivePixelCountFilterModelDelegate(StandardDeepableTreeModelDelegate):

	def _is_index_readonly(self, index: T) -> bool:
		model = index.model()
		key, value = model.key(index), model.value(index)
		filter_key, last_key = first_last_keys(key)
		# filter_data: FilterData = model[filter_key]
		# print(f"_is_index_readonly {last_key}")
		keys = deep_keys(NucleiParams)
		if index.column() == 1 and last_key in keys:
			return False
		return super()._is_index_readonly(index)


class PositivePixelCountFilterViewDelegateFactory(FilterTemplateItemViewDelegateFactory):

	def _create(self, index: T, filter_data) -> typing.Optional[AbstractItemViewDelegate[T, M, V]]:
		if isinstance(filter_data, F):
			return PositivePixelCountFilterViewDelegate()


class PositivePixelCountFilterViewDelegate(ImmutableFilterTemplateTreeViewDelegate):

	def filter_data_type(self, filter_data_dict: dict) -> type:
		return PositivePixelCountFilterData

	def _createEditor(self, parent: QWidget, option: QStyleOptionViewItem, index: T, key: str,
					  filter_data: F) -> QWidget:
		model = index.model()
		filter_key, last_key = first_last_keys(key)
		value = model.value(index)
		keys = deep_keys(NucleiParams)
		if last_key in keys:
			return super().createEditor(parent, option, index)
		else:
			return super()._createEditor(parent, option, index, key, filter_data)

	def _sizeHint(self, option: QStyleOptionViewItem, index: T, key: str) -> QSize:
		return super()._sizeHint(option, index, key)
