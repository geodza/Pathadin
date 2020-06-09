from common_image.model.color_mode import ColorMode
from common_qt.mvc.model.delegate.factory.item_model_delegate_factory import AbstractItemModelDelegateFactory
from common_qt.mvc.view.delegate.factory.abstract_item_view_context_menu_delegate_factory import \
	AbstractItemViewContextMenuDelegateFactory
from common_qt.mvc.view.delegate.factory.abstract_item_view_delegate_factory import AbstractItemViewDelegateFactory
from filter.common.filter_data_factory import FilterDataFactoryFactory, RuleBasedFilterDataFactory
from filter.filter_plugin import FilterPlugin, I, M, V, F
from filter.manual_threshold.gray_manual_threshold_filter.gray_manual_threshold_filter_processor import \
	GrayManualThresholdFilterProcessorFactory
from filter.manual_threshold.gray_manual_threshold_filter.gray_manual_threshold_filter_view_delegate import \
	GrayManualThresholdFilterViewDelegateFactory, \
	GrayManualThresholdFilterModelDelegate, GrayManualThresholdFilterContextMenuDelegateFactory
from filter.manual_threshold.manual_threshold_filter_model import GrayManualThresholdFilterData, \
	GrayManualThresholdFilterData_
from filter_processor.filter_processor_factory import FilterProcessorFactory
from filter_template.filter_item_model_delegate_rule import FilterItemModelDelegateRule
from filter_template.filter_template_item_model_delegate_factory import RuleBasedFilterTemplateItemModelDelegateFactory


class GrayManualThresholdFilterPlugin(FilterPlugin):
	plugin = True

	def itemModelDelegateFactory(self) -> AbstractItemModelDelegateFactory[I]:
		return RuleBasedFilterTemplateItemModelDelegateFactory(
			FilterItemModelDelegateRule(GrayManualThresholdFilterData, GrayManualThresholdFilterModelDelegate()))

	def itemViewDelegateFactory(self) -> AbstractItemViewDelegateFactory[I, M, V]:
		return GrayManualThresholdFilterViewDelegateFactory()

	def filterProcessorFactory(self) -> FilterProcessorFactory[F]:
		return GrayManualThresholdFilterProcessorFactory()

	def itemViewContextMenuDelegateFactory(self) -> AbstractItemViewContextMenuDelegateFactory[I, V]:
		return GrayManualThresholdFilterContextMenuDelegateFactory()

	def filterDataFactoryFactory(self) -> FilterDataFactoryFactory[F]:
		return RuleBasedFilterDataFactory(
			(GrayManualThresholdFilterData_.filter_type, GrayManualThresholdFilterData_.color_mode),
			{
				(GrayManualThresholdFilterData.filter_type, ColorMode.L): GrayManualThresholdFilterData,
			})
