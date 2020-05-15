from abc import ABC, abstractmethod

import typing
from PyQt5.QtCore import QModelIndex

from common_qt.mvc.delegate.item_model_delegate import QAbstractItemModelDelegate

T = typing.TypeVar('T', bound=QModelIndex)


class QAbstractItemModelDelegateFactory(ABC, typing.Generic[T]):

	@abstractmethod
	def create(self, index: T) -> typing.Optional[QAbstractItemModelDelegate[T]]:
		pass
