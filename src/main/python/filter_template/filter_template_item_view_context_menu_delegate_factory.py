from abc import ABC, abstractmethod

import typing

from common_qt.mvc.view.delegate.abstract_item_view_context_menu_delegate import AbstractItemViewContextMenuDelegate
from common_qt.mvc.view.delegate.factory.abstract_item_view_context_menu_delegate_factory import \
	AbstractItemViewContextMenuDelegateFactory
from common_qt.mvc.view.delegate.factory.abstract_item_view_delegate_factory import AbstractItemViewDelegateFactory, T
from common_qt.mvc.view.delegate.abstract_item_view_delegate import AbstractItemViewDelegate
from deepable.core import first_last_keys
from deepable_qt.model.deepable_model_index import DeepableQModelIndex
from deepable_qt.model.deepable_tree_model import DeepableTreeModel
from deepable_qt.view.deepable_tree_view import DeepableTreeView

I = DeepableQModelIndex
M = DeepableTreeModel
V = DeepableTreeView


class FilterTemplateItemViewContextMenuDelegateFactory(AbstractItemViewContextMenuDelegateFactory[I, V], ABC):

	def create_delegate(self, index: I, view: V) -> typing.Optional[AbstractItemViewContextMenuDelegate[I, V]]:
		model = index.model()
		if not index.isValid():
			return self._create_delegate(index, view, None)
		elif model is None:
			print("none model in FilterTemplateItemViewContextMenuDelegateFactory", index.isValid(), index.model(),
				  index.row(), index.column())
			# TODO Sometimes model is None. Find out when and why.
			# Cases: self.beginResetModel(), helpEvent()
			# When resetting model (like after changing type of filter), some indexes are invalidated and get here with model=None
			return super().create_delegate(index, view)
		else:
			key, value = model.key(index), model.value(index)
			filter_key, last_key = first_last_keys(key)
			filter_data = model[filter_key]
			return self._create_delegate(index, view, filter_data)

	@abstractmethod
	def _create_delegate(self, index: I, view: V, filter_data) -> typing.Optional[AbstractItemViewContextMenuDelegate[I, V]]:
		pass
