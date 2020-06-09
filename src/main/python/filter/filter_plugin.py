from abc import ABC, abstractmethod

import typing

from PyQt5.QtCore import QModelIndex, QAbstractItemModel
from PyQt5.QtWidgets import QAbstractItemView

from common.json_utils import JSONEncoderFactory, JSONDecoderFactory
from common_qt.mvc.model.delegate.factory.item_model_delegate_factory import AbstractItemModelDelegateFactory
from common_qt.mvc.view.delegate.factory.abstract_item_view_context_menu_delegate_factory import \
	AbstractItemViewContextMenuDelegateFactory
from common_qt.mvc.view.delegate.factory.abstract_item_view_delegate_factory import AbstractItemViewDelegateFactory
from filter.common.filter_data_factory import FilterDataFactoryFactory
from filter_processor.filter_processor_factory import FilterProcessorFactory
from filter.common.filter_model import FilterOutput, FilterData

I = typing.TypeVar('I', bound=QModelIndex)
M = typing.TypeVar('M', bound=QAbstractItemModel)
V = typing.TypeVar('V', bound=QAbstractItemView)

F = typing.TypeVar('F', bound=FilterData)
R = typing.TypeVar('R', bound=FilterOutput)


class FilterPlugin(ABC):

	@abstractmethod
	def itemModelDelegateFactory(self) -> AbstractItemModelDelegateFactory[I]:
		pass

	@abstractmethod
	def itemViewDelegateFactory(self) -> AbstractItemViewDelegateFactory[I, M, V]:
		pass

	@abstractmethod
	def itemViewContextMenuDelegateFactory(self) -> AbstractItemViewContextMenuDelegateFactory[I, V]:
		pass

	@abstractmethod
	def filterProcessorFactory(self) -> FilterProcessorFactory[F]:
		pass

	@abstractmethod
	def filterDataFactoryFactory(self) -> FilterDataFactoryFactory[F]:
		pass
