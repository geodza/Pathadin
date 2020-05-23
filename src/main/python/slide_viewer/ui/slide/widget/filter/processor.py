import typing

from filter.filter_plugin import FilterPlugin
from filter_processor.composite_filter_processor import CompositeFilterProcessor
from filter_processor.filter_processor import FilterProcessor
from img.filter.base_filter import FilterResults2

F = typing.TypeVar('F')
R = typing.TypeVar('R', bound=FilterResults2)


def create_filter_processor(filter_plugins: typing.List[FilterPlugin]) -> FilterProcessor:
	factories = [p.filterProcessorFactory() for p in filter_plugins]
	return CompositeFilterProcessor(factories)
