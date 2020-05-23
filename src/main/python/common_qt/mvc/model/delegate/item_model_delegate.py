from abc import ABC, abstractmethod

import typing
from PyQt5.QtCore import QModelIndex, Qt

T = typing.TypeVar('T', bound=QModelIndex)


class AbstractItemModelDelegate(ABC, typing.Generic[T]):

	@abstractmethod
	def flags(self, index: T) -> Qt.ItemFlags:
		pass

	@abstractmethod
	def data(self, index: T, role: int = Qt.DisplayRole) -> typing.Any:
		pass

	@abstractmethod
	def setData(self, index: T, value: typing.Any, role: int = Qt.DisplayRole) -> bool:
		pass
