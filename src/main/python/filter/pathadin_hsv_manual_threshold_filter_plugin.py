from common_image.model.color_mode import ColorMode
from common_qt.mvc.model.delegate.factory.item_model_delegate_factory import AbstractItemModelDelegateFactory
from common_qt.mvc.view.delegate.factory.abstract_item_view_context_menu_delegate_factory import \
	AbstractItemViewContextMenuDelegateFactory
from common_qt.mvc.view.delegate.factory.abstract_item_view_delegate_factory import AbstractItemViewDelegateFactory
from filter.common.filter_data_factory import FilterDataFactoryFactory, RuleBasedFilterDataFactory
from filter.filter_plugin import FilterPlugin, I, M, V, F
from filter.manual_threshold.hsv_manual_threshold_filter.hsv_manual_threshold_filter_processor import \
	HSVManualThresholdFilterProcessorFactory
from filter.manual_threshold.hsv_manual_threshold_filter.hsv_manual_threshold_filter_view_delegate import \
	HSVManualThresholdFilterModelDelegateFactory, \
	HSVManualThresholdFilterViewDelegateFactory, HSVManualThresholdFilterContextMenuDelegateFactory
from filter.manual_threshold.manual_threshold_filter_model import HSVManualThresholdFilterData_, \
	HSVManualThresholdFilterData
from filter_processor.filter_processor_factory import FilterProcessorFactory


class HSVManualThresholdFilterPlugin(FilterPlugin):
	plugin = True

	def itemModelDelegateFactory(self) -> AbstractItemModelDelegateFactory[I]:
		return HSVManualThresholdFilterModelDelegateFactory()

	def itemViewDelegateFactory(self) -> AbstractItemViewDelegateFactory[I, M, V]:
		return HSVManualThresholdFilterViewDelegateFactory()

	def filterProcessorFactory(self) -> FilterProcessorFactory[F]:
		return HSVManualThresholdFilterProcessorFactory()

	def itemViewContextMenuDelegateFactory(self) -> AbstractItemViewContextMenuDelegateFactory[I, V]:
		return HSVManualThresholdFilterContextMenuDelegateFactory()

	def filterDataFactoryFactory(self) -> FilterDataFactoryFactory[F]:
		return RuleBasedFilterDataFactory(
			(HSVManualThresholdFilterData_.filter_type, HSVManualThresholdFilterData_.color_mode),
			{
				(HSVManualThresholdFilterData.filter_type, ColorMode.HSV): HSVManualThresholdFilterData,
			})
