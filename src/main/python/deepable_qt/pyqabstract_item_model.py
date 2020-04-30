import collections
import copy
import typing
from typing import Iterator

from PyQt5.QtCore import QAbstractItemModel, QObject, QModelIndex, pyqtSignal
from dataclasses import dataclass, InitVar, FrozenInstanceError

from deepable.core import deep_keys, deep_get, deep_set, deep_del, Deepable, is_deepable, deep_diff, deep_get_default, \
	deep_key_index, deep_contains, deep_iter, deep_len, is_immutable, deep_new_key_index, DeepDiffChanges, \
	deep_index_key


@dataclass
class PyQAbstractItemModel(QAbstractItemModel):
	# Model for Deepable interface (Deepable interface is expressed through a set of deep_* functions).
	# Main principles:
	#   has Deepable root
	# 	key-value nature (2 columns) (with possible nesting)
	# 	get, set, delete through dict-like interface methods
	# 	operates on root only through deepable functions
	#   transforms rows signals to keys signals

	parent_: InitVar[typing.Optional[QObject]] = None

	keysChanged = pyqtSignal(list)
	keysRemoved = pyqtSignal(list)
	keysInserted = pyqtSignal(list)

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

	# self.dataChanged.connect(self.__on_data_changed)
	# self.rowsInserted.connect(self.__on_rows_inserted)
	# # rowsAboutToBeRemoved and not rowsRemoved because after rowsRemoved keys for corresponding rows will be already removed from root
	# self.rowsAboutToBeRemoved.connect(self.__on_rows_about_to_be_removed)

	def get_root(self) -> Deepable:
		raise NotImplementedError

	def set_root(self, root: Deepable) -> None:
		raise NotImplementedError

	def index(self, row: int, column: int, parent: QModelIndex = QModelIndex()) -> QModelIndex:
		if parent.isValid():
			parent_path, p = parent.internalPointer()
			parent_object = deep_get(self.get_root(), parent_path)
			index_path = parent_path + '.' + deep_index_key(parent_object, row)
		else:
			index_path = deep_index_key(self.get_root(), row)
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

	def columnCount(self, parent: QModelIndex = QModelIndex()) -> int:
		return 2

	def rowCount(self, parent: QModelIndex = QModelIndex()) -> int:
		if not parent.isValid():
			return deep_len(self.get_root())
		elif parent.column() == 1:
			return 0
		elif parent.column() == 0:
			val = self.value(parent)
			if is_deepable(val):
				return deep_len(val)
			else:
				return 0

	def key(self, index: QModelIndex) -> str:
		if index.isValid():
			key_ = index.internalPointer()[0]
			return key_
		else:
			raise ValueError("Invalid index")

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
		return deep_key_index(self.get_root(), key)

	def key_to_parent_index(self, key: str) -> QModelIndex:
		path = key.split('.')
		parent_obj = self.get_root()
		parent = QModelIndex()
		for key_ in path[:-1]:
			# row = list(deep_keys(parent_obj)).index(key_)
			row = deep_key_index(parent_obj, key_)
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

	def __getitem__(self, key: str) -> typing.Any:
		return deep_get(self.get_root(), key)

	def __len__(self) -> int:
		return deep_len(self.get_root())

	def __iter__(self) -> Iterator:
		return deep_iter(self.get_root())

	def __contains__(self, key: str):
		return deep_contains(self.get_root(), key)

	def __setitem__(self, key: str, value: typing.Any) -> None:
		try:
			old_value = deep_get(self.get_root(), key)
		except (KeyError, AttributeError):
			self.__insert_new_key(key, value)
		else:
			if is_deepable(old_value) or is_deepable(value):
				self.__edit_deepable(key, old_value, value)
			else:
				self.__edit_not_deepable(key, value)

	def __edit_not_deepable(self, key: str, value: typing.Any):
		row = self.key_to_row(key)
		parent_index = self.key_to_parent_index(key)
		deep_set(self.get_root(), key, value)
		self.dataChanged.emit(self.index(row, 0, parent_index), self.index(row, 1, parent_index))
		self.keysChanged.emit([key])

	def __insert_new_key(self, key: str, value: typing.Any) -> None:
		parent_index = self.key_to_parent_index(key)
		new_row = deep_new_key_index(self.get_root(), key)
		self.beginInsertRows(parent_index, new_row, new_row)
		deep_set(self.get_root(), key, value)
		self.endInsertRows()
		self.keysInserted.emit([key])

	def __edit_deepable(self, key: str, old_value: Deepable, value: Deepable):
		if self.__can_be_edited_by_parts(old_value, value):
			self.__edit_by_parts(key, old_value, value)
		else:
			df = deep_diff(old_value, value)
			if self.__can_be_edited_without_insert_remove_signals(df):
				self.__edit_without_insert_remove_signals(key, value, df)
			else:
				# We need signals about what indexes need to be removed and what indexes need to be inserted (for nested objects).
				# But we cant update immutable object so we need to delete and add it.
				self.__delete_then_add(key, value)

	def __can_be_edited_without_insert_remove_signals(self, df: DeepDiffChanges) -> bool:
		return not df.added and not df.removed

	def __edit_without_insert_remove_signals(self, key: str, value: Deepable, df: DeepDiffChanges):
		deep_set(self.get_root(), key, value)
		# edit by key as one big edit but for indexes it is many dataChanged signals
		for changed_key, diff_change in df.changed.items():
			changed_key_root = key + "." + changed_key
			row = self.key_to_row(changed_key_root)
			parent_index = self.key_to_parent_index(changed_key_root)
			self.dataChanged.emit(self.index(row, 0, parent_index), self.index(row, 1, parent_index))
		self.keysChanged.emit([key])

	def __can_be_edited_by_parts(self, old_value: Deepable, value: Deepable) -> bool:
		return type(old_value) == type(value) and not is_immutable(old_value)

	def __edit_by_parts(self, key: str, old_value: Deepable, value: Deepable):
		df = deep_diff(old_value, value)
		try:
			for removed_key in df.removed:
				removed_key_root = key + "." + removed_key
				row = self.key_to_row(removed_key_root)
				parent_index = self.key_to_parent_index(removed_key_root)
				self.beginRemoveRows(parent_index, row, row)
				deep_del(self.get_root(), removed_key_root)
				self.endRemoveRows()
				self.keysRemoved.emit([removed_key_root])
			for added_key, added_value in df.added.items():
				added_key_root = key + "." + added_key
				parent_index = self.key_to_parent_index(added_key_root)
				new_row = deep_new_key_index(self.get_root(), key)
				self.beginInsertRows(parent_index, new_row, new_row)
				deep_set(self.get_root(), added_key_root, added_value)
				self.endInsertRows()
				self.keysInserted.emit([added_key_root])
			for changed_key, diff_change in df.changed.items():
				changed_key_root = key + "." + changed_key
				row = self.key_to_row(changed_key_root)
				parent_index = self.key_to_parent_index(changed_key_root)
				deep_set(self.get_root(), changed_key_root, diff_change.new_value)
				self.dataChanged.emit(self.index(row, 0, parent_index), self.index(row, 1, parent_index))
				self.keysChanged.emit([changed_key_root])
		except FrozenInstanceError as e:
			# TODO
			raise ValueError(
				f"Deepable object {old_value} cant be edited. Attempted to modify immutable(frozen) object. deep_diff method must not dig into immutable objects.",
				e)

	def __delete_then_add(self, key: str, value: typing.Any):
		root = self.get_root()
		row = self.key_to_row(key)
		parent_index = self.key_to_parent_index(key)
		if parent_index.isValid():
			parent_key = self.key(parent_index)
			parent_object = self.value(parent_index)
			if isinstance(parent_object, collections.OrderedDict):
				# self.__delitem__(key)
				self.beginRemoveRows(parent_index, row, row)
				deep_del(root, key)
				self.endRemoveRows()
				items = list(parent_object.items())
				self.beginInsertRows(parent_index, row, row)
				items.insert(row, (key, value))
				new_ordered_dict = collections.OrderedDict(items)
				deep_set(root, parent_key, new_ordered_dict)
				self.endInsertRows()
			else:
				# self.__delitem__(key)
				self.beginRemoveRows(parent_index, row, row)
				deep_del(root, key)
				self.endRemoveRows()
				self.beginInsertRows(parent_index, row, row)
				deep_set(root, key, value)
				self.endInsertRows()
		else:
			self.beginResetModel()
			deep_set(root, key, value)
			self.endResetModel()

	def __delitem__(self, key: str) -> None:
		row = self.key_to_row(key)
		parent_index = self.key_to_parent_index(key)
		self.beginRemoveRows(parent_index, row, row)
		deep_del(self.get_root(), key)
		self.endRemoveRows()

	def clear(self) -> None:
		parent_index = QModelIndex()
		n_rows = len(self)
		if n_rows:
			self.beginRemoveRows(parent_index, 0, n_rows - 1)
			self.get_root().clear()
			self.endRemoveRows()
#
# def __on_data_changed(self, top_left: QModelIndex, bottom_right: QModelIndex):
# 	parent, first, last = top_left.parent(), top_left.row(), bottom_right.row()
# 	keys = self.key_range(parent, first, last)
# 	self.keysChanged.emit(keys)
#
# def __on_rows_about_to_be_removed(self, parent: QModelIndex, first: int, last: int) -> None:
# 	keys = self.key_range(parent, first, last)
# 	self.keysRemoved.emit(keys)
#
# def __on_rows_inserted(self, parent: QModelIndex, first: int, last: int) -> None:
# 	keys = self.key_range(parent, first, last)
# 	self.keysInserted.emit(keys)
#
# def key_range(self, parent: QModelIndex, first: int, last: int) -> list:
# 	if parent.isValid():
# 		children = [parent.child(row, 0) for row in range(first, last + 1)]
# 	else:
# 		children = [self.index(row, 0, QModelIndex()) for row in range(first, last + 1)]
# 	keys = self.indexes_to_keys(children)
# 	return keys

# def is_top_level(self, index: QModelIndex):
#     return not index.parent().isValid()
