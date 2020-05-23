from abc import ABC, abstractmethod

import typing

from common_qt.mvc.model.delegate.factory.item_model_delegate_factory import AbstractItemModelDelegateFactory
from common_qt.mvc.model.delegate.item_model_delegate import AbstractItemModelDelegate
from deepable_qt.model.deepable_model_index import DeepableQModelIndex
from filter_template.filter_item_model_delegate_rule import FilterItemModelDelegateRule

T = DeepableQModelIndex
F = typing.Any


class FilterTemplateItemModelDelegateFactory(AbstractItemModelDelegateFactory[T], ABC):

	def create(self, index: T) -> typing.Optional[AbstractItemModelDelegate[T]]:
		model = index.model()
		key, value = model.key(index), model.value(index)
		filter_key = key.split(".")[0]
		last_key = key.split(".")[-1]
		filter_data = model[filter_key]
		return self._create(index, filter_data)

	@abstractmethod
	def _create(self, index: T, filter_data: F) -> typing.Optional[AbstractItemModelDelegate[T]]:
		pass


class RuleBasedFilterTemplateItemModelDelegateFactory(FilterTemplateItemModelDelegateFactory, ABC):

	@abstractmethod
	def rule(self) -> FilterItemModelDelegateRule:
		pass

	def _create(self, index: T, filter_data: F) -> typing.Optional[AbstractItemModelDelegate[T]]:
		rule = self.rule()
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
