import typing

from PyQt5.QtCore import QModelIndex, Qt, QSize
from PyQt5.QtWidgets import QWidget, QStyleOptionViewItem

from common_qt.editor.dropdown import Dropdown, commit_close_after_dropdown_select
from common_qt.mvc.model.delegate.item_model_delegate import AbstractItemModelDelegate
from common_qt.mvc.view.delegate.item_view_delegate import AbstractItemViewDelegate
from deepable.core import deep_set, first_last_keys
from deepable_qt.model.deepable_model_index import DeepableQModelIndex
from deepable_qt.model.deepable_tree_model import DeepableTreeModel
from deepable_qt.model.standard_deepable_tree_model_delegate import StandardDeepableTreeModelDelegate
from deepable_qt.view.deepable_tree_view import DeepableTreeView
from filter_template.filter_template_item_model_delegate_factory import FilterTemplateItemModelDelegateFactory
from filter_template.filter_template_item_view_delegate import ImmutableFilterTemplateTreeViewDelegate
from filter_template.filter_template_item_viewl_delegate_factory import FilterTemplateItemViewDelegateFactory
from img.filter.base_filter import FilterData
from img.filter.kmeans_filter import KMeansFilterData, KMeansFilterData_, KMeansParams_, KMeansInitType

T = DeepableQModelIndex
M = DeepableTreeModel
V = DeepableTreeView
F = KMeansFilterData


class KMeansFilterModelDelegateFactory(FilterTemplateItemModelDelegateFactory):

	def _create(self, index: T, filter_data: F) -> typing.Optional[AbstractItemModelDelegate[T]]:
		if isinstance(filter_data, KMeansFilterData):
			return KMeansFilterModelDelegate()


class KMeansFilterModelDelegate(StandardDeepableTreeModelDelegate):

	def _is_index_readonly(self, index: T) -> bool:
		model = index.model()
		key, value = model.key(index), model.value(index)
		filter_key, last_key = first_last_keys(key)
		# filter_data: FilterData = model[filter_key]
		# print(f"_is_index_readonly {last_key}")
		if index.column() == 1 and last_key in (KMeansParams_.init, KMeansParams_.max_iter, KMeansParams_.n_clusters,
												KMeansParams_.n_init, KMeansParams_.precompute_distances,
												KMeansParams_.random_state, KMeansParams_.tol):
			return False
		return super()._is_index_readonly(index)


class KMeansFilterViewDelegateFactory(FilterTemplateItemViewDelegateFactory):

	def _create(self, index: T, filter_data) -> typing.Optional[AbstractItemViewDelegate[T, M, V]]:
		if isinstance(filter_data, F):
			return KMeansFilterViewDelegate()


class KMeansFilterViewDelegate(ImmutableFilterTemplateTreeViewDelegate):

	def filter_data_type(self, filter_data_dict: dict) -> type:
		return KMeansFilterData

	def _createEditor(self, parent: QWidget, option: QStyleOptionViewItem, index: T, key: str,
					  filter_data: F) -> QWidget:
		model = index.model()
		filter_key, last_key = first_last_keys(key)
		value = model.value(index)
		if last_key == KMeansParams_.init:
			dropdown = Dropdown(list(KMeansInitType), value, parent)
			return commit_close_after_dropdown_select(self._itd, dropdown)
		# elif key in (KMeansParams_.max_iter, KMeansParams_.n_clusters,
		# 			 KMeansParams_.n_init, KMeansParams_.precompute_distances,
		# 			 KMeansParams_.random_state, KMeansParams_.tol):
		# 	return super().createEditor(parent, option, index)

		return super()._createEditor(parent, option, index, key, filter_data)

	def _sizeHint(self, option: QStyleOptionViewItem, index: T, key: str) -> QSize:
		return super()._sizeHint(option, index, key)
