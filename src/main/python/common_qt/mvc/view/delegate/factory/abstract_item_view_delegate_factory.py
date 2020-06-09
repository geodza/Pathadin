import typing
from abc import ABC, abstractmethod

from PyQt5.QtCore import QModelIndex, QAbstractItemModel, pyqtSignal, QObject, Qt
from PyQt5.QtWidgets import QAbstractItemView

from common_qt.mvc.view.delegate.abstract_item_view_delegate import AbstractItemViewDelegate

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


class D(QObject):
	d = pyqtSignal(str)


class AbstractItemViewDelegateFactory(ABC, typing.Generic[T, M, V]):

	@abstractmethod
	def create(self, index: T) -> typing.Optional[AbstractItemViewDelegate[T, M, V]]:
		pass


if __name__ == '__main__':
	d = D()
	d2 = D()


	def f(x):
		print(x)

	d2.d.connect(f)


	d.d.connect(d2.d, type=Qt.AutoConnection | Qt.UniqueConnection)
	try:
		d.d.connect(d2.d, type=Qt.AutoConnection | Qt.UniqueConnection)
	except TypeError:
		pass
	d.d.emit("123")
