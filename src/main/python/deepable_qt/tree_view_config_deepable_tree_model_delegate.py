import re
from typing import Tuple, Optional, Any

from PyQt5.QtCore import Qt, QObject, QModelIndex, QVariant
from PyQt5.QtGui import QColor
from dataclasses import dataclass

from deepable.core import deep_keys, deep_get, Deepable, is_deepable, deep_contains
from deepable.convert import deep_to_dict
from deepable_qt.deepable_model_index import DeepableQModelIndex
from deepable_qt.deepable_tree_model import DeepableTreeModel
from deepable_qt.deepable_tree_model_delegate import DeepableTreeModelDelegate
from slide_viewer.ui.common.model import TreeViewConfig


@dataclass
class TreeViewConfigDeepableTreeModelDelegate(DeepableTreeModelDelegate):

	def data(self, index: DeepableQModelIndex, role: int = Qt.DisplayRole) -> Any:
		model = index.model()
		if index.column() == 0:
			key, value = model.key(index), model.value(index)
			if self.__has_tree_view_config(index):
				tree_view_config = deep_get(value, TreeViewConfig.snake_case_name)
				if role == Qt.DisplayRole:
					return self.__display_data(index, tree_view_config)
				elif role == Qt.DecorationRole:
					return self.__decoration_data(index, tree_view_config)
		return super().data(index, role)

	def __has_tree_view_config(self, index: DeepableQModelIndex) -> bool:
		model = index.model()
		key, obj = model.key(index), model.value(index)
		# obj = deep_get(self.root, key)
		return is_deepable(obj) and TreeViewConfig.snake_case_name in deep_keys(obj) and deep_get(obj,
																								  TreeViewConfig.snake_case_name)

	def __display_data(self, index: DeepableQModelIndex, view_config: TreeViewConfig) -> Any:
		model = index.model()
		key, obj = model.key(index), model.value(index)
		# obj = deep_get(self.root, key)
		return view_config.display_pattern.format_map(deep_to_dict(obj))

	def __decoration_data(self, index: DeepableQModelIndex,  view_config: TreeViewConfig) -> Any:
		model = index.model()
		key, obj = model.key(index), model.value(index)
		attr_key = view_config.decoration_attr
		if attr_key:
			color_str = model[key + '.' + attr_key]
			return QColor(color_str)
		return QVariant()
