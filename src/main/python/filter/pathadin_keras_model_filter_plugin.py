from common_qt.mvc.model.delegate.factory.item_model_delegate_factory import AbstractItemModelDelegateFactory
from common_qt.mvc.view.delegate.factory.abstract_item_view_context_menu_delegate_factory import \
	AbstractItemViewContextMenuDelegateFactory
from common_qt.mvc.view.delegate.factory.abstract_item_view_delegate_factory import AbstractItemViewDelegateFactory
from filter.common.filter_data_factory import FilterDataFactoryFactory, FilterTypeFilterDataFactory
from filter.filter_plugin import FilterPlugin, I, M, V, F, R
from filter.keras.keras_model_filter_model import KerasModelFilterData
from filter.keras.keras_model_filter_processor import KerasModelFilterProcessorFactory
from filter.keras.keras_model_filter_view_delegate import KerasModelFilterModelDelegateFactory, \
	KerasModelFilterViewDelegateFactory, KerasModelFilterContextMenuDelegateFactory
from filter_processor.filter_processor_factory import FilterProcessorFactory


class KerasModelFilterPlugin(FilterPlugin):
	plugin = True

	def itemModelDelegateFactory(self) -> AbstractItemModelDelegateFactory[I]:
		return KerasModelFilterModelDelegateFactory()

	def itemViewDelegateFactory(self) -> AbstractItemViewDelegateFactory[I, M, V]:
		return KerasModelFilterViewDelegateFactory()

	def filterProcessorFactory(self) -> FilterProcessorFactory[F]:
		return KerasModelFilterProcessorFactory()

	def itemViewContextMenuDelegateFactory(self) -> AbstractItemViewContextMenuDelegateFactory[I, V]:
		return KerasModelFilterContextMenuDelegateFactory()

	def filterDataFactoryFactory(self) -> FilterDataFactoryFactory[F]:
		return FilterTypeFilterDataFactory(KerasModelFilterData.filter_type, KerasModelFilterData)
