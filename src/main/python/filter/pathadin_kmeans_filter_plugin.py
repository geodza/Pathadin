from common.json_utils import JSONEncoderFactory, TypesBasedJSONEncoderFactory, JSONDecoderFactory
from common_qt.mvc.model.delegate.factory.item_model_delegate_factory import AbstractItemModelDelegateFactory
from common_qt.mvc.view.delegate.factory.abstract_item_view_context_menu_delegate_factory import \
	AbstractItemViewContextMenuDelegateFactory
from common_qt.mvc.view.delegate.factory.abstract_item_view_delegate_factory import AbstractItemViewDelegateFactory
from filter.common.filter_data_factory import FilterDataFactoryFactory, RuleBasedFilterDataFactory, \
	FilterTypeFilterDataFactory
from filter.filter_plugin import FilterPlugin, I, M, V, F, R
from filter.kmeans.kmeans_filter_model import KMeansFilterData, KMeansFilterData_
from filter.kmeans.kmeans_filter_processor import KMeansFilterProcessorFactory
from filter.kmeans.kmeans_filter_view_delegate import KMeansFilterModelDelegateFactory, KMeansFilterViewDelegateFactory, \
	KMeansFilterContextMenuDelegateFactory
from filter_processor.filter_processor_factory import FilterProcessorFactory


class KMeansFilterPlugin(FilterPlugin):
	plugin = True

	def itemModelDelegateFactory(self) -> AbstractItemModelDelegateFactory[I]:
		return KMeansFilterModelDelegateFactory()

	def itemViewDelegateFactory(self) -> AbstractItemViewDelegateFactory[I, M, V]:
		return KMeansFilterViewDelegateFactory()

	def itemViewContextMenuDelegateFactory(self) -> AbstractItemViewContextMenuDelegateFactory[I, V]:
		return KMeansFilterContextMenuDelegateFactory()

	def filterProcessorFactory(self) -> FilterProcessorFactory[F]:
		return KMeansFilterProcessorFactory()

	def filterDataFactoryFactory(self) -> FilterDataFactoryFactory[F]:
		return FilterTypeFilterDataFactory(KMeansFilterData.filter_type, KMeansFilterData)
