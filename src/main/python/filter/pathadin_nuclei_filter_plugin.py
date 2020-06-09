from common_qt.mvc.model.delegate.factory.item_model_delegate_factory import AbstractItemModelDelegateFactory
from common_qt.mvc.view.delegate.factory.abstract_item_view_context_menu_delegate_factory import \
	AbstractItemViewContextMenuDelegateFactory
from common_qt.mvc.view.delegate.factory.abstract_item_view_delegate_factory import AbstractItemViewDelegateFactory
from filter.common.filter_data_factory import FilterDataFactoryFactory, FilterTypeFilterDataFactory
from filter.filter_plugin import FilterPlugin, I, M, V, F, R
from filter.nuclei.nuclei_filter_model import NucleiFilterData, NucleiFilterData_
from filter.nuclei.nuclei_filter_processor import NucleiFilterProcessorFactory
from filter.nuclei.nuclei_filter_view_delegate import NucleiFilterModelDelegateFactory, NucleiFilterViewDelegateFactory, \
	NucleiFilterContextMenuDelegateFactory
from filter_processor.filter_processor_factory import FilterProcessorFactory


class NucleiFilterPlugin(FilterPlugin):
	plugin = True

	def itemModelDelegateFactory(self) -> AbstractItemModelDelegateFactory[I]:
		return NucleiFilterModelDelegateFactory()

	def itemViewDelegateFactory(self) -> AbstractItemViewDelegateFactory[I, M, V]:
		return NucleiFilterViewDelegateFactory()

	def filterProcessorFactory(self) -> FilterProcessorFactory[F]:
		return NucleiFilterProcessorFactory()

	def itemViewContextMenuDelegateFactory(self) -> AbstractItemViewContextMenuDelegateFactory[I, V]:
		return NucleiFilterContextMenuDelegateFactory()

	def filterDataFactoryFactory(self) -> FilterDataFactoryFactory[F]:
		return FilterTypeFilterDataFactory(NucleiFilterData.filter_type, NucleiFilterData)
