from common_qt.mvc.model.delegate.factory.item_model_delegate_factory import AbstractItemModelDelegateFactory
from common_qt.mvc.view.delegate.factory.abstract_item_view_context_menu_delegate_factory import \
	AbstractItemViewContextMenuDelegateFactory
from common_qt.mvc.view.delegate.factory.abstract_item_view_delegate_factory import AbstractItemViewDelegateFactory
from filter.common.filter_data_factory import FilterDataFactoryFactory, FilterTypeFilterDataFactory
from filter.filter_plugin import FilterPlugin, I, M, V, F, R
from filter.positive_pixel_count.positive_pixel_count_filter_model import PositivePixelCountFilterData
from filter.positive_pixel_count.positive_pixel_count_filter_processor import PositivePixelCountFilterProcessorFactory
from filter.positive_pixel_count.positive_pixel_count_filter_view_delegate import \
	PositivePixelCountFilterModelDelegateFactory, PositivePixelCountFilterViewDelegateFactory, \
	PositivePixelCountFilterContextMenuDelegateFactory
from filter_processor.filter_processor_factory import FilterProcessorFactory


class PositivePixelCountFilterPlugin(FilterPlugin):
	plugin = True

	def itemModelDelegateFactory(self) -> AbstractItemModelDelegateFactory[I]:
		return PositivePixelCountFilterModelDelegateFactory()

	def itemViewDelegateFactory(self) -> AbstractItemViewDelegateFactory[I, M, V]:
		return PositivePixelCountFilterViewDelegateFactory()

	def filterProcessorFactory(self) -> FilterProcessorFactory[F]:
		return PositivePixelCountFilterProcessorFactory()

	def itemViewContextMenuDelegateFactory(self) -> AbstractItemViewContextMenuDelegateFactory[I, V]:
		return PositivePixelCountFilterContextMenuDelegateFactory()

	def filterDataFactoryFactory(self) -> FilterDataFactoryFactory[F]:
		return FilterTypeFilterDataFactory(PositivePixelCountFilterData.filter_type, PositivePixelCountFilterData)
