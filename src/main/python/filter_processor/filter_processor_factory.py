from abc import ABC, abstractmethod
from typing import TypeVar, Generic

from filter_processor.filter_processor import FilterProcessor
from filter.common.filter_model import FilterOutput

F = TypeVar('F')


class FilterProcessorFactory(ABC, Generic[F]):

	@abstractmethod
	def create(self, filter_data: F) -> FilterProcessor[F]:
		pass
