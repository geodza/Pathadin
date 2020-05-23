import typing
from PyQt5.QtCore import QModelIndex, Qt
from dataclasses import dataclass, field

from common_qt.mvc.model.delegate.item_model_delegate import AbstractItemModelDelegate
from common_qt.mvc.model.delegate.factory.item_model_delegate_factory import AbstractItemModelDelegateFactory

T = typing.TypeVar('T', bound=QModelIndex)


@dataclass
class CompositeAbstractItemModelDelegate(AbstractItemModelDelegate[T]):
	factories: typing.List[AbstractItemModelDelegateFactory[T]] = field(default_factory=list)

	def find_delegate(self, index: T) -> AbstractItemModelDelegate[T]:
		for f in self.factories:
			d = f.create(index)
			if d is not None:
				return d
		raise ValueError(f"CompositeQAbstractItemModelDelegate. No appropriate delegate found in {self.factories}")

	def flags(self, index: T) -> Qt.ItemFlags:
		return self.find_delegate(index).flags(index)

	def data(self, index: T, role: int = Qt.DisplayRole) -> typing.Any:
		return self.find_delegate(index).data(index, role)

	def setData(self, index: T, value: typing.Any, role: int = Qt.DisplayRole) -> bool:
		return self.find_delegate(index).setData(index, value, role)
