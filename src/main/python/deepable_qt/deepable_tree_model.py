import re
from typing import Tuple, Optional, Any

from PyQt5.QtCore import Qt, QObject, QModelIndex, QVariant
from PyQt5.QtGui import QColor
from dataclasses import dataclass

from deepable.core import deep_keys, deep_get, Deepable, is_deepable
from deepable_qt.pyqabstract_item_model import PyQAbstractItemModel
from slide_viewer.ui.common.model import TreeViewConfig


@dataclass
class DeepableTreeModel(PyQAbstractItemModel):
    # TODO refactor. read_only_attrs was introduced for flat structure, but now it is deep and flat read_only_attrs is too weak
    read_only_attrs: Tuple = ()
    read_only_attr_pattern: str = None
    _root: Deepable = None

    def __post_init__(self, parent_: Optional[QObject]):
        super().__post_init__(parent_)
        # def dasd(self, read_only_attrs=(), parent: typing.Optional[QObject] = None) -> None:
        # super().__init__(self, parent)
        # HeaderAbstractItemModel.__init__(self, parent)
        # PyQAbstractItemModel.__init__(self, parent)

    def flags(self, index: QModelIndex) -> Qt.ItemFlags:
        flags = super().flags(index)
        flags |= Qt.ItemIsEditable
        if self.is_index_readonly(index):
            flags &= ~ Qt.ItemIsEditable
        return flags

    def setData(self, index: QModelIndex, value: Any, role: int = Qt.DisplayRole) -> bool:
        self[self.key(index)] = value
        return True

    def data(self, index: QModelIndex, role: int = Qt.DisplayRole) -> Any:
        if index.column() == 0:
            obj = self.value(index)
            if is_deepable(obj) and TreeViewConfig.snake_case_name in deep_keys(obj) and deep_get(obj,
                                                                                                  "tree_view_config"):
                key = self.key(index)
                return self.data_view_config(key, deep_get(obj, "tree_view_config"), role)
            else:
                key = self.key(index).split('.')[-1]
                return self.data_plain(key, role)
        elif index.column() == 1:
            obj = self.value(index)
            if is_deepable(obj):
                return QVariant()
            else:
                return self.data_plain(obj, role)

    @property
    def root(self) -> Deepable:
        return self._root

    @root.setter
    def root(self, root: Deepable) -> None:
        self.beginResetModel()
        self._root = root
        self.endResetModel()

    # def set_root(self, root: Deepable) -> None:
    #     self.beginResetModel()
    #     self.root = root
    #     self.endResetModel()

    def get_root(self) -> Deepable:
        return self.root

    def is_index_readonly(self, index: QModelIndex) -> bool:
        is_readonly = False
        is_readonly |= index.column() == 0
        is_readonly |= bool(re.match(self.read_only_attr_pattern, self.key(index))) if self.read_only_attr_pattern else False
        is_readonly |= is_deepable(self.value(index))
        return is_readonly

    def data_view_config(self, parent_path: str, view_config: TreeViewConfig, role: int = Qt.DisplayRole):
        if role == Qt.DisplayRole:
            attr_key_names = view_config.display_attrs or []
            values = list(map(lambda k: deep_get(self.root, parent_path + '.' + k), attr_key_names))
            values_str = "\n".join(map(str, values))
            return values_str
        elif role == Qt.DecorationRole:
            attr_key = view_config.decoration_attr
            if attr_key:
                color_str = deep_get(self.root, parent_path + '.' + attr_key)
                return QColor(color_str)
        else:
            return QVariant()

    def data_plain(self, value: object, role: int = Qt.DisplayRole):
        if role == Qt.DisplayRole:
            return str(value)
        elif role == Qt.EditRole:
            return value
        return QVariant()
