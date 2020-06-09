import typing
from PyQt5.QtCore import QModelIndex, Qt, QAbstractItemModel
from PyQt5.QtWidgets import QAbstractItemView

from common_qt.mvc.view.delegate.factory.abstract_item_view_delegate_factory import AbstractItemViewDelegateFactory
from common_qt.mvc.view.delegate.abstract_item_view_delegate import AbstractItemViewDelegate

T = typing.TypeVar('T', bound=QModelIndex)
M = typing.TypeVar('M', bound=QAbstractItemModel)
V = typing.TypeVar('V', bound=QAbstractItemView)


class StandardItemViewDelegateFactory(AbstractItemViewDelegateFactory):
	def create(self, index: T) -> typing.Optional[AbstractItemViewDelegate]:
		return AbstractItemViewDelegate()
