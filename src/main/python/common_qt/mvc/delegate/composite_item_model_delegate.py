import typing
from PyQt5.QtCore import QModelIndex, Qt
from dataclasses import dataclass, field

from common_qt.mvc.delegate.item_model_delegate import QAbstractItemModelDelegate
from common_qt.mvc.delegate.factory.item_model_delegate_factory import QAbstractItemModelDelegateFactory

T = typing.TypeVar('T', bound=QModelIndex)


@dataclass
class QAbstractItemModelDelegateCompositeFactoryDelegate(QAbstractItemModelDelegate[T]):
	factories: typing.List[QAbstractItemModelDelegateFactory[T]] = field(default_factory=list)

	def findDelegate(self, index: T) -> QAbstractItemModelDelegate[T]:
		for f in self.factories:
			d = f.create(index)
			if d is not None:
				return d
		raise ValueError("No appropriate delegate found")

	def flags(self, index: T) -> Qt.ItemFlags:
		return self.findDelegate(index).flags(index)

	def data(self, index: T, role: int = Qt.DisplayRole) -> typing.Any:
		return self.findDelegate(index).data(index, role)

	def setData(self, index: T, value: typing.Any, role: int = Qt.DisplayRole) -> bool:
		return self.findDelegate(index).setData(index, value, role)
