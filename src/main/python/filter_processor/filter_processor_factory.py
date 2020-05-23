from abc import ABC, abstractmethod
from typing import TypeVar, Generic

from filter_processor.filter_processor import FilterProcessor
from img.filter.base_filter import FilterResults2

F = TypeVar('F')
R = TypeVar('R', bound=FilterResults2)


class FilterProcessorFactory(ABC, Generic[F, R]):

	@abstractmethod
	def create(self, filter_data: F) -> FilterProcessor[F, R]:
		pass
