from common_qt.mvc.model.delegate.factory.item_model_delegate_factory import AbstractItemModelDelegateFactory
from common_qt.mvc.view.delegate.factory.item_view_delegate_factory import AbstractItemViewDelegateFactory
from filter.filter_plugin import FilterPlugin, T, M, V, F, R
from filter.nuclei.nuclei_filter_processor import NucleiFilterProcessorFactory
from filter.nuclei.nuclei_filter_view_delegate import NucleiFilterModelDelegateFactory, NucleiFilterViewDelegateFactory
from filter_processor.filter_processor_factory import FilterProcessorFactory


class NucleiFilterPlugin(FilterPlugin):
	plugin = True

	def itemModelDelegateFactory(self) -> AbstractItemModelDelegateFactory[T]:
		return NucleiFilterModelDelegateFactory()

	def itemViewDelegateFactory(self) -> AbstractItemViewDelegateFactory[T, M, V]:
		return NucleiFilterViewDelegateFactory()

	def filterProcessorFactory(self) -> FilterProcessorFactory[F, R]:
		return NucleiFilterProcessorFactory()
