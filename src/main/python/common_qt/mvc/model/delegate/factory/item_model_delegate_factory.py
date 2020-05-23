from abc import ABC, abstractmethod

import typing
from PyQt5.QtCore import QModelIndex

from common_qt.mvc.model.delegate.item_model_delegate import AbstractItemModelDelegate

T = typing.TypeVar('T', bound=QModelIndex)


class AbstractItemModelDelegateFactory(ABC, typing.Generic[T]):

	@abstractmethod
	def create(self, index: T) -> typing.Optional[AbstractItemModelDelegate[T]]:
		pass
