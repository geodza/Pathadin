from abc import ABC, abstractmethod

import typing

from PyQt5.QtCore import QModelIndex, QAbstractItemModel
from PyQt5.QtWidgets import QAbstractItemView

from common_qt.mvc.model.delegate.factory.item_model_delegate_factory import AbstractItemModelDelegateFactory
from common_qt.mvc.view.delegate.factory.item_view_delegate_factory import AbstractItemViewDelegateFactory
from filter_processor.filter_processor_factory import FilterProcessorFactory
from img.filter.base_filter import FilterResults2

T = typing.TypeVar('T', bound=QModelIndex)
M = typing.TypeVar('M', bound=QAbstractItemModel)
V = typing.TypeVar('V', bound=QAbstractItemView)

F = typing.TypeVar('F')
R = typing.TypeVar('R', bound=FilterResults2)


class FilterPlugin(ABC):

	@abstractmethod
	def itemModelDelegateFactory(self) -> AbstractItemModelDelegateFactory[T]:
		pass

	@abstractmethod
	def itemViewDelegateFactory(self) -> AbstractItemViewDelegateFactory[T, M, V]:
		pass

	@abstractmethod
	def filterProcessorFactory(self) -> FilterProcessorFactory[F, R]:
		pass
