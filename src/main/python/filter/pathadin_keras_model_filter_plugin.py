from common_qt.mvc.model.delegate.factory.item_model_delegate_factory import AbstractItemModelDelegateFactory
from common_qt.mvc.view.delegate.factory.item_view_delegate_factory import AbstractItemViewDelegateFactory
from filter.filter_plugin import FilterPlugin, T, M, V, F, R
from filter.keras.keras_model_filter_view_delegate import KerasModelFilterModelDelegateFactory, \
	KerasModelFilterViewDelegateFactory
from filter_processor.filter_processor_factory import FilterProcessorFactory
from filter.keras.keras_model_filter_processor import KerasModelFilterProcessorFactory


class KerasModelFilterPlugin(FilterPlugin):
	plugin = True

	def itemModelDelegateFactory(self) -> AbstractItemModelDelegateFactory[T]:
		return KerasModelFilterModelDelegateFactory()

	def itemViewDelegateFactory(self) -> AbstractItemViewDelegateFactory[T, M, V]:
		return KerasModelFilterViewDelegateFactory()

	def filterProcessorFactory(self) -> FilterProcessorFactory[F, R]:
		return KerasModelFilterProcessorFactory()
