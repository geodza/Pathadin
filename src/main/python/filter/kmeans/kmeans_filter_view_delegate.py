import typing

from PyQt5.QtCore import QSize, QModelIndex
from PyQt5.QtWidgets import QWidget, QStyleOptionViewItem, QMenu

from common_qt.action.my_menu import create_menu
from common_qt.editor.dropdown import Dropdown, commit_close_after_dropdown_select
from common_qt.mvc.model.delegate.item_model_delegate import AbstractItemModelDelegate
from common_qt.mvc.view.delegate.abstract_item_view_context_menu_delegate import AbstractItemViewContextMenuDelegate
from common_qt.mvc.view.delegate.abstract_item_view_delegate import AbstractItemViewDelegate
from deepable.core import first_last_keys
from deepable_qt.model.deepable_model_index import DeepableQModelIndex
from deepable_qt.model.deepable_tree_model import DeepableTreeModel
from deepable_qt.view.deepable_tree_view import DeepableTreeView
from filter.kmeans.kmeans_filter_model import KMeansInitType, KMeansParams_, KMeansFilterData
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
F = KMeansFilterData


def is_top_level(index: QModelIndex) -> bool:
	return not index.parent().isValid()


class KMeansFilterContextMenuDelegateFactory(FilterTemplateItemViewContextMenuDelegateFactory):

	def _create_delegate(self, index: I, view: V, filter_data) -> typing.Optional[
		AbstractItemViewContextMenuDelegate[I, V]]:
		if not index.isValid():
			return KMeansFilterContextMenuDelegate(view)
		elif isinstance(filter_data, KMeansFilterData):
			return KMeansFilterContextMenuDelegate(view)
		else:
			return None


class KMeansFilterContextMenuDelegate(FilterTemplateItemViewContextMenuDelegate):

	def create_menu(self, index: I) -> typing.Optional[QMenu]:
		actions = []
		# Index may be invalid => no model for invalid index. So take model from view.
		model = self.view.model()
		if not index.isValid():
			add_action = self.create_add_action("Add kmeans filter", "kmeans_filter_", lambda k: KMeansFilterData(k, k))
			actions.append(add_action)
			menu = create_menu("KMeans", actions)
			return menu
		else:
			return None


class KMeansFilterModelDelegateFactory(FilterTemplateItemModelDelegateFactory):

	def _create(self, index: I, filter_data: F) -> typing.Optional[AbstractItemModelDelegate[I]]:
		if isinstance(filter_data, KMeansFilterData):
			return KMeansFilterModelDelegate()


class KMeansFilterModelDelegate(FilterTemplateItemModelDelegate):

	def _is_index_readonly(self, index: I) -> bool:
		model = index.model()
		key, value = model.key(index), model.value(index)
		filter_key, last_key = first_last_keys(key)
		# filter_data: FilterData = model[filter_key]
		# print(f"_is_index_readonly {last_key}")
		if index.column() == 1 and last_key in (KMeansParams_.init, KMeansParams_.max_iter, KMeansParams_.n_clusters,
												KMeansParams_.n_init, KMeansParams_.random_state, KMeansParams_.tol, 'columns'):
			return False
		return super()._is_index_readonly(index)


class KMeansFilterViewDelegateFactory(FilterTemplateItemViewDelegateFactory):

	def _create(self, index: I, filter_data) -> typing.Optional[AbstractItemViewDelegate[I, M, V]]:
		if isinstance(filter_data, F):
			return KMeansFilterViewDelegate()


class KMeansFilterViewDelegate(ImmutableFilterTemplateTreeViewDelegate):

	def filter_data_type(self, filter_data_dict: dict) -> type:
		return KMeansFilterData

	def _createEditor(self, parent: QWidget, option: QStyleOptionViewItem, index: I, key: str,
					  filter_data: F) -> QWidget:
		model = index.model()
		filter_key, last_key = first_last_keys(key)
		value = model.value(index)
		if last_key == KMeansParams_.init:
			dropdown = Dropdown(list(KMeansInitType), value, parent)
			return commit_close_after_dropdown_select(self, dropdown)
		# elif key in (KMeansParams_.max_iter, KMeansParams_.n_clusters,
		# 			 KMeansParams_.n_init,
		# 			 KMeansParams_.random_state, KMeansParams_.tol):
		# 	return super().createEditor(parent, option, index)

		return super()._createEditor(parent, option, index, key, filter_data)

	def _sizeHint(self, option: QStyleOptionViewItem, index: I, key: str) -> QSize:
		return super()._sizeHint(option, index, key)

# def menus(self, index: T) -> typing.List[QMenu]:
# 	m = QMenu()
# 	if not index.isValid():
# 		m.addAction(QAction("Add kmeans filter"))
# 	return [m]
