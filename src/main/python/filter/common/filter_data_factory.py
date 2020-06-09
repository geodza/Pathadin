from abc import ABC, abstractmethod
from enum import Enum
from typing import TypeVar, Generic, Optional, Tuple, Dict, Any, Type

from dacite import from_dict, Config
from dataclasses import dataclass

from filter.common.filter_model import FilterData, FilterData_

F = TypeVar('F', bound=FilterData)


class FilterDataFactory(ABC, Generic[F]):

	@abstractmethod
	def create_filter_data(self, filter_data_dict: dict) -> F:
		pass


class FilterDataFactoryFactory(ABC, Generic[F]):

	@abstractmethod
	def create_factory(self, filter_data_dict: dict) -> Optional[FilterDataFactory[F]]:
		pass


# class TemplateFilterDataFactoryFactory(FilterDataFactoryFactory, Generic[F]):
#
# 	def __init__(self, filter_types: Set[str], filter_data_factory: FilterDataFactory[F]):
# 		self.filter_types = filter_types
# 		self.filter_data_factory = filter_data_factory
#
# 	def create_factory(self, filter_type: str) -> Optional[FilterDataFactory[F]]:
# 		if filter_type in self.filter_types:
# 			return self.filter_data_factory
# 		else:
# 			return None
#

# @abstractmethod
# def filter_hierarchy(self) -> typing.Dict[str, typing.Any]:
# 	pass


@dataclass
class RuleBasedFilterDataFactory(FilterDataFactory[F], FilterDataFactoryFactory[F], Generic[F]):
	rule_def: Tuple[str, ...]
	rule_value_to_type: Dict[Tuple[Any, ...], Type[F]]

	def create_factory(self, filter_data_dict: dict) -> Optional[FilterDataFactory[F]]:
		rule_value = tuple(filter_data_dict.get(prop, None) for prop in self.rule_def)
		if rule_value in self.rule_value_to_type:
			return self
		else:
			# print("self.rule_value_to_type, rule_value", self.rule_value_to_type, rule_value)
			return None

	def create_filter_data(self, filter_data_dict: dict) -> F:
		rule_value = tuple(filter_data_dict.get(prop, None) for prop in self.rule_def)
		type_ = self.rule_value_to_type.get(rule_value)
		return from_dict(type_, filter_data_dict, config=Config(cast=[Enum, Tuple]))


@dataclass
class FilterTypeFilterDataFactory(FilterDataFactory[F], FilterDataFactoryFactory[F], Generic[F]):
	filter_type: str
	type_: Type[F]

	def create_factory(self, filter_data_dict: dict) -> Optional[FilterDataFactory[F]]:
		filter_type = filter_data_dict.get(FilterData_.filter_type, None)
		if filter_type == self.filter_type:
			return self
		else:
			# print("self.filter_type, required type:", self.filter_type, filter_type)
			return None

	def create_filter_data(self, filter_data_dict: dict) -> F:
		return from_dict(self.type_, filter_data_dict, config=Config(cast=[Enum]))
