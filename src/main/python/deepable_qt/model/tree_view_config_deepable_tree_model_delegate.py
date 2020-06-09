import typing
from typing import Any

from PyQt5.QtCore import Qt, QVariant, QSize, QItemSelectionRange
from PyQt5.QtGui import QColor
from dataclasses import dataclass

from common_qt.mvc.model.delegate.factory.item_model_delegate_factory import AbstractItemModelDelegateFactory
from common_qt.mvc.model.delegate.item_model_delegate import AbstractItemModelDelegate
from deepable.convert import deep_to_dict
from deepable.core import deep_keys, deep_get, is_deepable
from deepable_qt.model.deepable_model_index import DeepableQModelIndex
from deepable_qt.model.standard_deepable_tree_model_delegate import StandardDeepableTreeModelDelegate
from annotation.model import TreeViewConfig

I = DeepableQModelIndex


class TreeViewConfigDeepableTreeModelDelegateFactory(AbstractItemModelDelegateFactory[I]):

	def create(self, index: I) -> typing.Optional[AbstractItemModelDelegate[I]]:
		return TreeViewConfigDeepableTreeModelDelegate()


@dataclass
class TreeViewConfigDeepableTreeModelDelegate(StandardDeepableTreeModelDelegate):

	def data(self, index: I, role: int = Qt.DisplayRole) -> Any:
		model = index.model()
		if index.column() == 0:
			key, value = model.key(index), model.value(index)
			if self.__has_tree_view_config(index):
				tree_view_config = deep_get(value, TreeViewConfig.snake_case_name)
				if role == Qt.DisplayRole:
					return self.__display_data(index, tree_view_config)
				elif role == Qt.DecorationRole:
					return self.__decoration_data(index, tree_view_config)
				elif role == Qt.SizeHintRole:
					size = tree_view_config.decoration_size
					if size:
						return QSize(int(size), int(size))

		return super().data(index, role)

	def __has_tree_view_config(self, index: I) -> bool:
		model = index.model()
		key, obj = model.key(index), model.value(index)
		# obj = deep_get(self.root, key)
		return is_deepable(obj) and TreeViewConfig.snake_case_name in deep_keys(obj) and deep_get(obj,
																								  TreeViewConfig.snake_case_name)

	def __display_data(self, index: I, view_config: TreeViewConfig) -> Any:
		model = index.model()
		key, obj = model.key(index), model.value(index)
		# obj = deep_get(self.root, key)
		return view_config.display_pattern.format_map(deep_to_dict(obj))

	def __decoration_data(self, index: I, view_config: TreeViewConfig) -> Any:
		model = index.model()
		key, obj = model.key(index), model.value(index)
		attr_key = view_config.decoration_attr
		if attr_key:
			color_str = model[key + '.' + attr_key]
			return QColor(color_str)
		return QVariant()

	def on_data_changed(self, topLeft: I, bottomRight: I, roles: typing.Iterable[int]) -> None:
		index_range = QItemSelectionRange(topLeft, bottomRight)
		indexes = index_range.indexes()
		for index in indexes:

			model = index.model()
			key = model.key(index)
			last_key = key.split('.')[-1]
			if last_key == "decoration_size" and index.column() == 1:
				first_key = key.split('.', 1)[0]
				annotation_index = model.key_to_index(first_key, 0)
				# print("index.data(Qt.DecorationRole)",  annotation_index.data(Qt.DecorationRole))
				# print("index.data(Qt.SizeHintRole)",  annotation_index.data(Qt.SizeHintRole))
				# value = model[key]
				# size = int(value)
				model.dataChanged.emit(annotation_index, annotation_index, [Qt.SizeHintRole])
	# super().setData(index, size, role)
	# model.dataChanged.emit(annotation_index, annotation_index)
