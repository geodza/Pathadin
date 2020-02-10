import typing
from typing import Iterator

from PyQt5.QtCore import QAbstractItemModel, QObject, QModelIndex, pyqtSignal
from dataclasses import dataclass, InitVar, FrozenInstanceError

from slide_viewer.ui.odict.deep.base.deepable import deep_keys, deep_get, deep_set, deep_del, Deepable, is_deepable


@dataclass
class PyQAbstractItemModel(QAbstractItemModel):
    parent_: InitVar[typing.Optional[QObject]] = None

    objectsChanged = pyqtSignal(list)
    objectsRemoved = pyqtSignal(list)
    objectsInserted = pyqtSignal(list)

    def __post_init__(self, parent_: typing.Optional[QObject]):
        # super().__init__(parent)
        QAbstractItemModel.__init__(self, parent_)
        # https://www.riverbankcomputing.com/pipermail/pyqt/2007-April/015842.html
        # Qt requires method "parent(self, index: QModelIndex) -> QModelIndex"
        # To find out parent of index, we need to store info about parent in index.
        # "internalPointer" is the place were we can store info about parent.
        # The problems with "internalPointer" are:
        # 1) we cant store integer because it would be interpreted as address and program will crash
        # 2) we can store object in it, but we need to keep reference to this object because qt will not
        self.pyqt_bug_weak_ref_dict = {}
        self.dataChanged.connect(self.on_data_changed)
        self.rowsInserted.connect(self.on_rows_inserted)
        self.rowsAboutToBeRemoved.connect(self.on_rows_about_to_be_removed)

    def get_root(self) -> Deepable:
        raise NotImplementedError

    def index(self, row: int, column: int, parent: QModelIndex = QModelIndex()) -> QModelIndex:
        if parent.isValid():
            parent_path, p = parent.internalPointer()
            parent_odict = deep_get(self.get_root(), parent_path)
            key_ = list(deep_keys(parent_odict))[row]
            index_path = parent_path + '.' + key_
        else:
            key_ = deep_keys(self.get_root())[row]
            index_path = key_
        self.pyqt_bug_weak_ref_dict.setdefault(index_path, [index_path, parent])
        index_path_list = self.pyqt_bug_weak_ref_dict[index_path]
        # print(f'{row}, {column} {index_path_list}')
        # we have to store info about position to be able to restore
        # it in parent() method (qt model-view requirement)
        return self.createIndex(row, column, index_path_list)

    def parent(self, index: QModelIndex) -> QModelIndex:
        # print(index.row(), index.column(), index.internalPointer())
        index_path, p = index.internalPointer()
        keys = index_path.split('.')
        if len(keys) == 1:
            return QModelIndex()
        else:
            return p
            # parent_path = '.'.join(keys[:-1])
            # self.pyqt_bug_weak_ref_dict.setdefault(parent_path, [parent_path])
            # parent_path_list = self.pyqt_bug_weak_ref_dict[parent_index_path]
            # return self.createIndex(parent_index_path[-1], 0, parent_path_list)
        # return QModelIndex()

    def columnCount(self, parent: QModelIndex = QModelIndex()) -> int:
        return 2

    def rowCount(self, parent: QModelIndex = QModelIndex()) -> int:
        if not parent.isValid():
            return len(deep_keys(self.get_root()))
        elif parent.column() == 1:
            return 0
        elif parent.column() == 0:
            val = self.value(parent)
            if is_deepable(val):
                return len(deep_keys(val))
            else:
                return 0

    def key(self, index: QModelIndex) -> str:
        if index.isValid():
            key_ = index.internalPointer()[0]
            return key_
        else:
            raise ValueError("Invalid index")
            # return ''

    def indexes_to_keys(self, indexes: typing.Iterable[QModelIndex]) -> typing.List[str]:
        return list(map(self.key, indexes))

    def value(self, index: QModelIndex) -> typing.Any:
        if index.isValid():
            key_ = index.internalPointer()[0]
            value_ = deep_get(self.get_root(), key_)
            return value_
        else:
            return self.get_root()

    def key_to_row(self, key: str) -> int:
        *parent_path, child_key = key.split('.')
        parent_key = '.'.join(parent_path)
        root = self.get_root()
        parent_odict: Deepable = deep_get(root, parent_key) if parent_key else root
        row = deep_keys(parent_odict).index(child_key)
        return row

    def key_to_parent_index(self, key: str) -> QModelIndex:
        path = key.split('.')
        parent_obj = self.get_root()
        parent = QModelIndex()
        for key_ in path[:-1]:
            row = list(deep_keys(parent_obj)).index(key_)
            parent = self.index(row, 0, parent)
            parent_obj = deep_get(parent_obj, key_)
        return parent

    def key_to_index(self, key: str, column: int = 0) -> QModelIndex:
        row = self.key_to_row(key)
        parent = self.key_to_parent_index(key)
        if parent.isValid():
            return parent.child(row, column)
        else:
            return self.index(row, column, QModelIndex())

    def __setitem__(self, key: str, value: typing.Any) -> None:
        parent_index = self.key_to_parent_index(key)
        *leading_keys, last_key = key.split('.')
        # parent_path = '.'.join(leading_keys)
        # parent_obj = deep_get(self.get_root(), parent_path)
        parent_obj = self.value(parent_index)
        if last_key in deep_keys(parent_obj):
            old_value = deep_get(parent_obj, last_key)
            if False and old_value is not None and is_deepable(old_value):
                try:
                    old_keys = set(deep_keys(old_value)) if is_deepable(old_value) else set()
                    new_keys = set(deep_keys(value)) if is_deepable(value) else set()
                    to_delete = old_keys - new_keys
                    to_update = old_keys & new_keys
                    to_add = new_keys - old_keys
                    for child_key in to_delete:
                        del self[key + '.' + child_key]
                    for child_key in to_update:
                        self[key + '.' + child_key] = deep_get(value, child_key)
                    for child_key in to_add:
                        self[key + '.' + child_key] = deep_get(value, child_key)
                except (FrozenInstanceError, TypeError):
                    deep_set(parent_obj, last_key, value)
                    row = self.key_to_row(key)
                    self.dataChanged.emit(self.index(row, 0, parent_index), self.index(row, 1, parent_index))
                except Exception:
                    raise ValueError(
                        f"cant edit key {key}\nwith value: {value}\nleading_keys: {leading_keys}\nlast_key: {last_key}\nold_value: {old_value}\nvalue : {value}")
            else:
                deep_set(parent_obj, last_key, value)
                row = self.key_to_row(key)
                # print(f"key: {key} last_key: {last_key}")
                self.dataChanged.emit(self.index(row, 0, parent_index), self.index(row, 1, parent_index))
        else:
            new_row = self.rowCount(parent_index)
            self.beginInsertRows(parent_index, new_row, new_row)
            deep_set(parent_obj, last_key, value)
            self.endInsertRows()

    def clear(self) -> None:
        parent_index = QModelIndex()
        n_rows = len(deep_keys(self.get_root()))
        if n_rows:
            self.beginRemoveRows(parent_index, 0, n_rows - 1)
            self.get_root().clear()
            self.endRemoveRows()

    def __delitem__(self, key: str) -> None:
        row = self.key_to_row(key)
        parent_index = self.key_to_parent_index(key)
        self.beginRemoveRows(parent_index, row, row)
        deep_del(self.get_root(), key)
        self.endRemoveRows()
        self.resetInternalData()

    def __getitem__(self, key: str) -> typing.Any:
        return deep_get(self.get_root(), key)

    def __len__(self) -> int:
        return len(deep_keys(self.get_root()))

    def __iter__(self) -> Iterator:
        return iter(deep_keys(self.get_root()))

    def __contains__(self, key: str):
        return key in deep_keys(self.get_root())

    def on_data_changed(self, top_left: QModelIndex, bottom_right: QModelIndex):
        parent, first, last = top_left.parent(), top_left.row(), bottom_right.row()
        children = [self.index(row, 0, parent) for row in range(first, last + 1)]
        keys = self.indexes_to_keys(children)
        self.objectsChanged.emit(keys)

    def on_rows_about_to_be_removed(self, parent: QModelIndex, first: int, last: int) -> None:
        if parent.isValid():
            children = [parent.child(row, 0) for row in range(first, last + 1)]
        else:
            children = [self.index(row, 0, QModelIndex()) for row in range(first, last + 1)]
        keys = self.indexes_to_keys(children)
        self.objectsRemoved.emit(keys)

    def on_rows_inserted(self, parent: QModelIndex, first: int, last: int) -> None:
        if parent.isValid():
            children = [parent.child(row, 0) for row in range(first, last + 1)]
        else:
            children = [self.index(row, 0, QModelIndex()) for row in range(first, last + 1)]
        keys = self.indexes_to_keys(children)
        self.objectsInserted.emit(keys)

# def is_top_level(self, index: QModelIndex):
#     return not index.parent().isValid()
