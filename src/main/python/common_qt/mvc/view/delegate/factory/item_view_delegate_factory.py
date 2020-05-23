from abc import ABC, abstractmethod

import typing
from PyQt5.QtCore import QModelIndex, QAbstractItemModel
from PyQt5.QtWidgets import QStyledItemDelegate, QAbstractItemView

from common_qt.mvc.view.delegate.item_view_delegate import AbstractItemViewDelegate

T = typing.TypeVar('T', bound=QModelIndex)
M = typing.TypeVar('M', bound=QAbstractItemModel)
V = typing.TypeVar('V', bound=QAbstractItemView)


class A(typing.Generic[T]):
	def a(self, t: T):
		pass


class Q(QModelIndex):
	pass


class AA(A[Q]):

	def a(self, t: T):
		super().a(t)


class AbstractItemViewDelegateFactory(ABC, typing.Generic[T, M, V]):

	@abstractmethod
	def create(self, index: T) -> typing.Optional[AbstractItemViewDelegate[T, M, V]]:
		pass
