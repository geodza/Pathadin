import typing
from PyQt5.QtCore import QModelIndex

from deepable_qt.deepable_tree_model import DeepableTreeModel


class DeepableQModelIndex(QModelIndex):
	def model(self) -> DeepableTreeModel:
		return typing.cast(DeepableTreeModel, super().model())
