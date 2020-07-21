import typing
from abc import ABC, abstractmethod

from PyQt5.QtCore import Qt

from common_qt.mvc.model.delegate.factory.item_model_delegate_factory import AbstractItemModelDelegateFactory
from common_qt.mvc.model.delegate.item_model_delegate import AbstractItemModelDelegate
from deepable.core import first_last_keys
from deepable_qt.model.deepable_model_index import DeepableQModelIndex
from deepable_qt.model.standard_deepable_tree_model_delegate import StandardDeepableTreeModelDelegate
from filter.common.filter_data import FilterData, FilterData_
from filter_template.filter_item_model_delegate_rule import FilterItemModelDelegateRule

I = DeepableQModelIndex
F = typing.Any


class FilterTemplateItemModelDelegateFactory(AbstractItemModelDelegateFactory[I], ABC):

	def create(self, index: I) -> typing.Optional[AbstractItemModelDelegate[I]]:
		model = index.model()
		key, value = model.key(index), model.value(index)
		filter_key = key.split(".")[0]
		last_key = key.split(".")[-1]
		filter_data = model[filter_key]
		return self._create(index, filter_data)

	@abstractmethod
	def _create(self, index: I, filter_data: F) -> typing.Optional[AbstractItemModelDelegate[I]]:
		pass


class FilterTemplateItemModelDelegate(StandardDeepableTreeModelDelegate):

	def data(self, index: I, role: int = Qt.DisplayRole) -> typing.Any:
		if role == Qt.DisplayRole and index.column() == 0:
			model = index.model()
			key, value = model.key(index), model.value(index)
			if isinstance(value, FilterData):
				return value.label

		return super().data(index, role)

	def _is_index_readonly(self, index: I) -> bool:
		model = index.model()
		if model:
			key, value = model.key(index), model.value(index)
			filter_key, last_key = first_last_keys(key)
			if last_key in (FilterData_.filter_type, FilterData_.id):
				return True
		return super()._is_index_readonly(index)


class RuleBasedFilterTemplateItemModelDelegateFactory(FilterTemplateItemModelDelegateFactory):

	def __init__(self, rule: FilterItemModelDelegateRule):
		self.rule = rule

	def _create(self, index: I, filter_data: F) -> typing.Optional[AbstractItemModelDelegate[I]]:
		rule = self.rule
		source = type(filter_data)
		if rule.source == source:
			return rule.target

# def filter_template_item_model_delegate_factory_rule(filter_type: type,
# 													 delegate_factory: typing.Callable[
# 														 [], AbstractItemModelDelegate[T]]):
# 	def wrapper(method):
# 		def _impl(self, index: T, filter_data):
# 			source = type(filter_data)
# 			if filter_type == source:
# 				return delegate_factory()
#
# 		return _impl
#
# 	return wrapper
