import collections
import copy
import typing
from typing import Iterator

from PyQt5.QtCore import QAbstractItemModel, QObject, QModelIndex, pyqtSignal
from dataclasses import dataclass, InitVar, FrozenInstanceError

from deepable.core import deep_keys, deep_get, deep_set, deep_del, Deepable, is_deepable, deep_diff, deep_get_default, \
	deep_key_order, deep_contains, deep_iter, deep_len, is_immutable


@dataclass
class PyQAbstractItemModel(QAbstractItemModel):
	# Model for Deepable interface (Deepable interface is expressed through a set of deep_* functions).
	# Main principles:
	#   has Deepable root
	# 	key-value nature (2 columns) (with possible nesting)
	# 	operates on root only through deepable functions
	# 	operates on root by keys: get, edit, delete
	#   transforms rows signals to keys signals

	# modelAboutToBeReset
	parent_: InitVar[typing.Optional[QObject]] = None

	__modelAboutToBeResetCopy: typing.Optional[Deepable] = None

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

		self.dataChanged.connect(self.__on_data_changed)
		self.rowsInserted.connect(self.__on_rows_inserted)
		# rowsAboutToBeRemoved and not rowsRemoved because after rowsRemoved keys for corresponding rows will be already removed from root
		self.rowsAboutToBeRemoved.connect(self.__on_rows_about_to_be_removed)

	def get_root(self) -> Deepable:
		raise NotImplementedError

	def set_root(self, root: Deepable) -> None:
		raise NotImplementedError

	def index(self, row: int, column: int, parent: QModelIndex = QModelIndex()) -> QModelIndex:
		if parent.isValid():
			parent_path, p = parent.internalPointer()
			parent_odict = deep_get(self.get_root(), parent_path)
			keys = list(deep_keys(parent_odict))
			key_ = keys[row]
			index_path = parent_path + '.' + key_
		else:
			keys = list(deep_keys(self.get_root()))
			key_ = keys[row]
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
		return deep_key_order(self.get_root(), key)

	def key_to_parent_index(self, key: str) -> QModelIndex:
		path = key.split('.')
		parent_obj = self.get_root()
		parent = QModelIndex()
		for key_ in path[:-1]:
			# row = list(deep_keys(parent_obj)).index(key_)
			row = deep_key_order(parent_obj, key_)
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
		# parent_index = self.key_to_parent_index(key)
		# parent_obj = self.value(parent_index)
		root = self.get_root()
		try:
			old_value = deep_get(root, key)
		except (KeyError, AttributeError):
			parent_index = self.key_to_parent_index(key)
			new_row = self.rowCount(parent_index)
			self.beginInsertRows(parent_index, new_row, new_row)
			deep_set(self.get_root(), key, value)
			self.endInsertRows()
		else:
			# if (is_immutable(old_value) or is_immutable(value)) and old_value!=value:
			# 	row = self.key_to_row(key)
			# 	parent_index = self.key_to_parent_index(key)
			# 	deep_set(parent_obj, key, value)
			# 	self.dataChanged.emit(self.index(row, 0, parent_index), self.index(row, 1, parent_index))
			# el
			if is_deepable(old_value) and is_deepable(value):
				self.__edit_deepable(key, old_value, value)
			elif type(old_value) is type(value):
				row = self.key_to_row(key)
				parent_index = self.key_to_parent_index(key)
				deep_set(root, key, value)
				self.dataChanged.emit(self.index(row, 0, parent_index), self.index(row, 1, parent_index))
			else:
				self.__delete_then_add(key, value)

	def __edit_deepable(self, key: str, old_value: typing.Any, value: typing.Any):
		parent_obj = self.get_root()
		if (is_immutable(old_value) or is_immutable(value)) and old_value != value:
			self.__delete_then_add(key, value)
			return
		df = deep_diff(old_value, value)
		try:
			for removed_key in df.removed:
				removed_key_root = key + "." + removed_key
				row = self.key_to_row(removed_key_root)
				parent_index = self.key_to_parent_index(removed_key_root)
				self.beginRemoveRows(parent_index, row, row)
				# try:
				deep_del(parent_obj, removed_key_root)
				# except FrozenInstanceError:
				# 	self.endRemoveRows()
				# 	self.__delete_then_add(key, value)
				# else:
				self.endRemoveRows()
			for added_key, added_value in df.added.items():
				added_key_root = key + "." + added_key
				parent_index = self.key_to_parent_index(added_key_root)
				# TODO we can add only to the end?
				# *leading_keys, last_key = added_key_root.split('.')
				new_row = self.rowCount(parent_index)
				# new_row_parent_key = '.'.join(leading_keys)
				# new_row_parent_index = self.key_to_parent_index(new_row_parent_key)
				self.beginInsertRows(parent_index, new_row, new_row)
				deep_set(parent_obj, added_key_root, added_value)
				self.endInsertRows()
			for changed_key, diff_change in df.changed.items():
				changed_key_root = key + "." + changed_key
				row = self.key_to_row(changed_key_root)
				parent_index = self.key_to_parent_index(changed_key_root)
				deep_set(parent_obj, changed_key_root, diff_change.new_value)
				self.dataChanged.emit(self.index(row, 0, parent_index), self.index(row, 1, parent_index))
		except FrozenInstanceError:
			if not df.added and not df.removed:
				root = self.get_root()
				deep_set(root, key, value)
				for changed_key, diff_change in df.changed.items():
					changed_key_root = key + "." + changed_key
					row = self.key_to_row(changed_key_root)
					parent_index = self.key_to_parent_index(changed_key_root)
					self.dataChanged.emit(self.index(row, 0, parent_index), self.index(row, 1, parent_index))
			else:
				# We need signals about what indexes need to be removed and what indexes need to be inserted (for nested objects).
				# Deepable object update by parts has failed so instead of add/delete nested(child) indexes we will delete index itself and add it again(with new value).
				self.__delete_then_add(key, value)

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

	def __on_data_changed(self, top_left: QModelIndex, bottom_right: QModelIndex):
		parent, first, last = top_left.parent(), top_left.row(), bottom_right.row()
		keys = self.key_range(parent, first, last)
		self.keysChanged.emit(keys)

	def __on_rows_about_to_be_removed(self, parent: QModelIndex, first: int, last: int) -> None:
		keys = self.key_range(parent, first, last)
		self.keysRemoved.emit(keys)

	def __on_rows_inserted(self, parent: QModelIndex, first: int, last: int) -> None:
		keys = self.key_range(parent, first, last)
		self.keysInserted.emit(keys)

	def key_range(self, parent: QModelIndex, first: int, last: int) -> list:
		if parent.isValid():
			children = [parent.child(row, 0) for row in range(first, last + 1)]
		else:
			children = [self.index(row, 0, QModelIndex()) for row in range(first, last + 1)]
		keys = self.indexes_to_keys(children)
		return keys

# def is_top_level(self, index: QModelIndex):
#     return not index.parent().isValid()
