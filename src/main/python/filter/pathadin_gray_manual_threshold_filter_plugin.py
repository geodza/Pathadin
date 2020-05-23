from common_qt.mvc.model.delegate.factory.item_model_delegate_factory import AbstractItemModelDelegateFactory
from common_qt.mvc.view.delegate.factory.item_view_delegate_factory import AbstractItemViewDelegateFactory
from filter.filter_plugin import FilterPlugin, T, M, V, F, R
from filter.manual_threshold.gray_manual_threshold_filter.gray_manual_threshold_filter_processor import \
	GrayManualThresholdFilterProcessorFactory
from filter.manual_threshold.gray_manual_threshold_filter.gray_manual_threshold_filter_view_delegate import \
	GrayManualThresholdFilterModelDelegateFactory, GrayManualThresholdFilterViewDelegateFactory
from filter_processor.filter_processor_factory import FilterProcessorFactory


class GrayManualThresholdFilterPlugin(FilterPlugin):
	plugin = True

	def itemModelDelegateFactory(self) -> AbstractItemModelDelegateFactory[T]:
		return GrayManualThresholdFilterModelDelegateFactory()

	def itemViewDelegateFactory(self) -> AbstractItemViewDelegateFactory[T, M, V]:
		return GrayManualThresholdFilterViewDelegateFactory()

	def filterProcessorFactory(self) -> FilterProcessorFactory[F, R]:
		return GrayManualThresholdFilterProcessorFactory()
