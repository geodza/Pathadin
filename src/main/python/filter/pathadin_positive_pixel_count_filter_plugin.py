from common_qt.mvc.model.delegate.factory.item_model_delegate_factory import AbstractItemModelDelegateFactory
from common_qt.mvc.view.delegate.factory.item_view_delegate_factory import AbstractItemViewDelegateFactory
from filter.filter_plugin import FilterPlugin, T, M, V, F, R
from filter.positive_pixel_count.positive_pixel_count_filter_view_delegate import \
	PositivePixelCountFilterModelDelegateFactory, PositivePixelCountFilterViewDelegateFactory
from filter_processor.filter_processor_factory import FilterProcessorFactory
from filter.positive_pixel_count.positive_pixel_count_filter_processor import PositivePixelCountFilterProcessorFactory


class PositivePixelCountFilterPlugin(FilterPlugin):
	plugin = True

	def itemModelDelegateFactory(self) -> AbstractItemModelDelegateFactory[T]:
		return PositivePixelCountFilterModelDelegateFactory()

	def itemViewDelegateFactory(self) -> AbstractItemViewDelegateFactory[T, M, V]:
		return PositivePixelCountFilterViewDelegateFactory()

	def filterProcessorFactory(self) -> FilterProcessorFactory[F, R]:
		return PositivePixelCountFilterProcessorFactory()
