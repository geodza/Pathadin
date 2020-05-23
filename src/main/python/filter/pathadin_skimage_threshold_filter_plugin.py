from common_qt.mvc.model.delegate.factory.item_model_delegate_factory import AbstractItemModelDelegateFactory
from common_qt.mvc.view.delegate.factory.item_view_delegate_factory import AbstractItemViewDelegateFactory
from filter.filter_plugin import FilterPlugin, T, M, V, F, R
from filter_processor.filter_processor_factory import FilterProcessorFactory
from filter.skimage_threshold.skimage_threshold_filter_processor import SkimageThresholdFilterProcessorFactory
from filter.skimage_threshold.skimage_threshold_filter_view_delegate import SkimageThresholdFilterModelDelegateFactory, \
	SkimageThresholdFilterViewDelegateFactory


class SkimageThresholdFilterPlugin(FilterPlugin):
	plugin = True

	def itemModelDelegateFactory(self) -> AbstractItemModelDelegateFactory[T]:
		return SkimageThresholdFilterModelDelegateFactory()

	def itemViewDelegateFactory(self) -> AbstractItemViewDelegateFactory[T, M, V]:
		return SkimageThresholdFilterViewDelegateFactory()

	def filterProcessorFactory(self) -> FilterProcessorFactory[F, R]:
		return SkimageThresholdFilterProcessorFactory()
