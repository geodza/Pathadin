from common_qt.mvc.model.delegate.factory.item_model_delegate_factory import AbstractItemModelDelegateFactory
from common_qt.mvc.view.delegate.factory.abstract_item_view_context_menu_delegate_factory import \
	AbstractItemViewContextMenuDelegateFactory
from common_qt.mvc.view.delegate.factory.abstract_item_view_delegate_factory import AbstractItemViewDelegateFactory
from filter.common.filter_data_factory import FilterDataFactoryFactory, RuleBasedFilterDataFactory
from filter.filter_plugin import FilterPlugin, I, M, V, F, R
from filter.skimage_threshold.skimage_threshold_filter_model import SkimageThresholdType, SkimageThresholdFilterData_, \
	SkimageMinimumThresholdFilterData, \
	SkimageMeanThresholdFilterData, SkimageThresholdFilterData
from filter.skimage_threshold.skimage_threshold_filter_processor import SkimageThresholdFilterProcessorFactory
from filter.skimage_threshold.skimage_threshold_filter_view_delegate import SkimageThresholdFilterModelDelegateFactory, \
	SkimageThresholdFilterViewDelegateFactory, SkimageThresholdFilterContextMenuDelegateFactory
from filter_processor.filter_processor_factory import FilterProcessorFactory


class SkimageThresholdFilterPlugin(FilterPlugin):
	plugin = True

	def itemModelDelegateFactory(self) -> AbstractItemModelDelegateFactory[I]:
		return SkimageThresholdFilterModelDelegateFactory()

	def itemViewDelegateFactory(self) -> AbstractItemViewDelegateFactory[I, M, V]:
		return SkimageThresholdFilterViewDelegateFactory()

	def filterProcessorFactory(self) -> FilterProcessorFactory[F]:
		return SkimageThresholdFilterProcessorFactory()

	def itemViewContextMenuDelegateFactory(self) -> AbstractItemViewContextMenuDelegateFactory[I, V]:
		return SkimageThresholdFilterContextMenuDelegateFactory()

	def filterDataFactoryFactory(self) -> FilterDataFactoryFactory[F]:
		return RuleBasedFilterDataFactory(
			(SkimageThresholdFilterData_.filter_type, SkimageThresholdFilterData_.skimage_threshold_type),
			{
				(SkimageThresholdFilterData.filter_type, SkimageThresholdType.threshold_minimum): SkimageMinimumThresholdFilterData,
				(SkimageThresholdFilterData.filter_type, SkimageThresholdType.threshold_mean): SkimageMeanThresholdFilterData
			})

# def filterHierarchy(self) -> typing.Dict[str, list]:
# 	return {
# 		"skimage": [
# 			{
# 				SkimageThresholdType.threshold_minimum: []
# 			},
# 			{
# 				SkimageThresholdType.threshold_mean: []
# 			}
# 		]
# 	}
