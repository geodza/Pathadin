from abc import ABC, abstractmethod

import typing

from common_qt.mvc.view.delegate.factory.item_view_delegate_factory import AbstractItemViewDelegateFactory, T
from common_qt.mvc.view.delegate.item_view_delegate import AbstractItemViewDelegate
from deepable.core import first_last_keys
from deepable_qt.model.deepable_model_index import DeepableQModelIndex
from deepable_qt.model.deepable_tree_model import DeepableTreeModel
from deepable_qt.view.deepable_tree_view import DeepableTreeView

T = DeepableQModelIndex
M = DeepableTreeModel
V = DeepableTreeView


class FilterTemplateItemViewDelegateFactory(AbstractItemViewDelegateFactory[T, M, V], ABC):

	def create(self, index: T) -> typing.Optional[AbstractItemViewDelegate[T, M, V]]:
		model = index.model()
		if model is None:
			print("none model", index.isValid(), index.model(), index.row(), index.column())
			# TODO Sometimes model is None. Find out when and why.
			# Cases: self.beginResetModel(), helpEvent()
			# When resetting model (like after changing type of filter), some indexes are invalidated and get here with model=None
			return super().create(index)
		key, value = model.key(index), model.value(index)
		filter_key, last_key = first_last_keys(key)
		filter_data = model[filter_key]
		return self._create(index, filter_data)

	@abstractmethod
	def _create(self, index: T, filter_data) -> typing.Optional[AbstractItemViewDelegate[T, M, V]]:
		pass
