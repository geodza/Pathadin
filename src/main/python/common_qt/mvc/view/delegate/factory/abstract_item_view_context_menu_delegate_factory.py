import typing
from abc import ABC, abstractmethod

from PyQt5.QtCore import QModelIndex, QAbstractItemModel
from PyQt5.QtWidgets import QAbstractItemView

from common_qt.mvc.view.delegate.abstract_item_view_context_menu_delegate import AbstractItemViewContextMenuDelegate

I = typing.TypeVar('I', bound=QModelIndex)
V = typing.TypeVar('V', bound=QAbstractItemView)


class AbstractItemViewContextMenuDelegateFactory(ABC, typing.Generic[I, V]):

	@abstractmethod
	def create_delegate(self, index: I, view: V) -> typing.Optional[AbstractItemViewContextMenuDelegate[I, V]]:
		pass
