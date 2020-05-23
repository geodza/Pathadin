from common_qt.mvc.model.delegate.factory.item_model_delegate_factory import AbstractItemModelDelegateFactory
from common_qt.mvc.view.delegate.factory.item_view_delegate_factory import AbstractItemViewDelegateFactory
from filter.filter_plugin import FilterPlugin, T, M, V, F, R
from filter.manual_threshold.hsv_manual_threshold_filter.hsv_manual_threshold_filter_processor import \
	HSVManualThresholdFilterProcessorFactory
from filter.manual_threshold.hsv_manual_threshold_filter.hsv_manual_threshold_filter_view_delegate import HSVManualThresholdFilterModelDelegateFactory, \
	HSVManualThresholdFilterViewDelegateFactory
from filter_processor.filter_processor_factory import FilterProcessorFactory


class HSVManualThresholdFilterPlugin(FilterPlugin):
	plugin = True

	def itemModelDelegateFactory(self) -> AbstractItemModelDelegateFactory[T]:
		return HSVManualThresholdFilterModelDelegateFactory()

	def itemViewDelegateFactory(self) -> AbstractItemViewDelegateFactory[T, M, V]:
		return HSVManualThresholdFilterViewDelegateFactory()

	def filterProcessorFactory(self) -> FilterProcessorFactory[F, R]:
		return HSVManualThresholdFilterProcessorFactory()
