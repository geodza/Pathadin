import typing
from typing import TypeVar

from dataclasses import field, dataclass

from filter.common.filter_data_factory import FilterDataFactory, FilterDataFactoryFactory
from filter.common.filter_data import FilterData

F = TypeVar('F', bound=FilterData)


@dataclass
class CompositeFilterDataFactory(FilterDataFactoryFactory[F], FilterDataFactory[F]):
	factories: typing.List[FilterDataFactoryFactory[F]] = field(default_factory=list)

	def find_factory(self, filter_data_dict: dict) -> FilterDataFactory[F]:
		for f in self.factories:
			d = f.create_factory(filter_data_dict)
			if d is not None:
				return d
		raise ValueError(
			f"CompositeFilterDataFactory. No appropriate factory found for {filter_data_dict} in {self.factories}")

	def create_filter_data(self, filter_data_dict: dict) -> F:
		return self.find_factory(filter_data_dict).create_filter_data(filter_data_dict)

	# def filter_hierarchy(self) -> typing.Dict[str, typing.Any]:
	# 	filter_hierarchy = {}
	# 	for f in self.factories:
	# 		h = f.filter_hierarchy()
	# 		filter_hierarchy.update(h)
	# 	return filter_hierarchy

	def create_factory(self, filter_data_dict: dict) -> FilterDataFactory[F]:
		return self.find_factory(filter_data_dict)
