import re
from typing import Tuple, Optional, Any

from PyQt5.QtCore import Qt, QObject, QModelIndex, QVariant
from PyQt5.QtGui import QColor
from dataclasses import dataclass

from deepable.core import deep_keys, deep_get, Deepable, is_deepable, deep_contains
from deepable.convert import deep_to_dict
from deepable_qt.pyqabstract_item_model import PyQAbstractItemModel
from slide_viewer.ui.common.model import TreeViewConfig


@dataclass
class DeepableTreeModel(PyQAbstractItemModel):
	read_only_attr_pattern: str = None

	def __post_init__(self, parent_: Optional[QObject]):
		super().__post_init__(parent_)

	def is_index_readonly(self, index: QModelIndex) -> bool:
		is_readonly=any([])
		is_readonly = False
		is_readonly |= index.column() == 0
		is_readonly |= bool(
			re.match(self.read_only_attr_pattern, self.key(index))) if self.read_only_attr_pattern else False
		return is_readonly

	def data(self, index: QModelIndex, role: int = Qt.DisplayRole) -> Any:
		if index.column() == 0:
			key, value = self.key(index), self.value(index)
			if self.has_tree_view_config(key):
				tree_view_config = deep_get(value, TreeViewConfig.snake_case_name)
				if role == Qt.DisplayRole:
					return self.display_data(key, tree_view_config)
				elif role == Qt.DecorationRole:
					return self.decoration_data(key, tree_view_config)
		return super().data(index, role)

	def has_tree_view_config(self, key: str) -> bool:
		obj = deep_get(self.root, key)
		return is_deepable(obj) and TreeViewConfig.snake_case_name in deep_keys(obj) and deep_get(obj,
																								  TreeViewConfig.snake_case_name)

	def display_data(self, key: str, view_config: TreeViewConfig) -> Any:
		obj = deep_get(self.root, key)
		return view_config.display_pattern.format_map(deep_to_dict(obj))

	def decoration_data(self, key: str, view_config: TreeViewConfig) -> Any:
		attr_key = view_config.decoration_attr
		if attr_key:
			color_str = deep_get(self.root, key + '.' + attr_key)
			return QColor(color_str)
		return QVariant()
