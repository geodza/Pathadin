from common_qt.mvc.model.delegate.factory.item_model_delegate_factory import AbstractItemModelDelegateFactory
from common_qt.mvc.view.delegate.factory.item_view_delegate_factory import AbstractItemViewDelegateFactory
from filter.filter_plugin import FilterPlugin, T, M, V, F, R
from filter.kmeans.kmeans_filter_view_delegate import KMeansFilterModelDelegateFactory, KMeansFilterViewDelegateFactory
from filter_processor.filter_processor_factory import FilterProcessorFactory
from filter.kmeans.kmeans_filter_processor import KMeansFilterProcessorFactory


class KMeansFilterPlugin(FilterPlugin):
	plugin = True

	def itemModelDelegateFactory(self) -> AbstractItemModelDelegateFactory[T]:
		return KMeansFilterModelDelegateFactory()

	def itemViewDelegateFactory(self) -> AbstractItemViewDelegateFactory[T, M, V]:
		return KMeansFilterViewDelegateFactory()

	def filterProcessorFactory(self) -> FilterProcessorFactory[F, R]:
		return KMeansFilterProcessorFactory()
