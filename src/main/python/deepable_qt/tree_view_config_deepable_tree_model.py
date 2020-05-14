import re
from typing import Tuple, Optional, Any

from PyQt5.QtCore import Qt, QObject, QModelIndex, QVariant
from PyQt5.QtGui import QColor
from dataclasses import dataclass

from deepable.core import deep_keys, deep_get, Deepable, is_deepable, deep_contains
from deepable.convert import deep_to_dict
from deepable_qt.deepable_tree_model import DeepableTreeModel
from slide_viewer.ui.common.model import TreeViewConfig


@dataclass
class TreeViewConfigDeepableTreeModel(DeepableTreeModel):

	def __post_init__(self, parent_: Optional[QObject]):
		super().__post_init__(parent_)

	def data(self, index: QModelIndex, role: int = Qt.DisplayRole) -> Any:
		if index.column() == 0:
			key, value = self.key(index), self.value(index)
			if self.__has_tree_view_config(key):
				tree_view_config = deep_get(value, TreeViewConfig.snake_case_name)
				if role == Qt.DisplayRole:
					return self.__display_data(key, tree_view_config)
				elif role == Qt.DecorationRole:
					return self.__decoration_data(key, tree_view_config)
		return super().data(index, role)

	def __has_tree_view_config(self, key: str) -> bool:
		obj = deep_get(self.root, key)
		return is_deepable(obj) and TreeViewConfig.snake_case_name in deep_keys(obj) and deep_get(obj,
																								  TreeViewConfig.snake_case_name)

	def __display_data(self, key: str, view_config: TreeViewConfig) -> Any:
		obj = deep_get(self.root, key)
		return view_config.display_pattern.format_map(deep_to_dict(obj))\

	def __decoration_data(self, key: str, view_config: TreeViewConfig) -> Any:
		attr_key = view_config.decoration_attr
		if attr_key:
			color_str = deep_get(self.root, key + '.' + attr_key)
			return QColor(color_str)
		return QVariant()
