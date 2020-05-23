import typing
from PyQt5.QtCore import QModelIndex, Qt, QVariant, QAbstractItemModel

from common_qt.mvc.model.delegate.factory.item_model_delegate_factory import AbstractItemModelDelegateFactory
from common_qt.mvc.model.delegate.item_model_delegate import AbstractItemModelDelegate
from deepable.convert import type_for_key
from deepable.core import is_deepable, deep_supports_key_delete, deep_supports_key_add
from deepable_qt.model.deepable_model_index import DeepableQModelIndex

T = DeepableQModelIndex


class StandardDeepableTreeModelDelegateFactory(AbstractItemModelDelegateFactory[T]):

	def create(self, index: T) -> typing.Optional[AbstractItemModelDelegate[T]]:
		return StandardDeepableTreeModelDelegate()


class StandardDeepableTreeModelDelegate(AbstractItemModelDelegate[T]):

	def flags(self, index: T) -> Qt.ItemFlags:
		model = index.model()
		flags = QAbstractItemModel.flags(model, index)
		flags |= Qt.ItemIsEditable
		if self._is_index_readonly(index):
			flags &= ~ Qt.ItemIsEditable
		return flags

	def _is_index_readonly(self, index: T) -> bool:
		# It is not a model-api method, it is a private helper method for flags method.
		# It represents index editability only in context of flags method.
		# If you override flags method and do not use __is_index_readonly in it
		# then __is_index_readonly will reflect nothing (will be useless).
		model = index.model()
		is_readonly = False
		if index.column() == 0:
			parent_value = model.value(index.parent())
			if not (deep_supports_key_delete(parent_value) and deep_supports_key_add(parent_value)):
				return True
		elif index.column() == 1:
			value = model.value(index)
			if value is not None and not isinstance(value, (str, int, float, bool)):
				return True
			elif value is None:
				parent_value = model.value(index.parent())
				key = model.key(index).split(".")[-1]
				key_type = type_for_key(type(parent_value), key)
				# print(f"{key} of type {key_type}")
				if not issubclass(key_type, (str, int, float, bool)):
					# print(f"{key} of type {key_type} is read_only")
					return True

		return is_readonly

	def data(self, index: T, role: int = Qt.DisplayRole) -> typing.Any:
		# role can be EditRole - it will be setted to itemProperty of editor (after createEditor call)
		model = index.model()
		if index.column() == 0:
			key = model.key(index).split('.')[-1]
			return self.__data_plain_value(key, role)
		elif index.column() == 1:
			obj = model.value(index)
			if role == Qt.EditRole:
				return obj
			else:
				if is_deepable(obj):
					return QVariant()
				else:
					return self.__data_plain_value(obj, role)

	def __data_plain_value(self, value: object, role: int = Qt.DisplayRole):
		if role == Qt.DisplayRole:
			return str(value)
		elif role == Qt.EditRole:
			return value
		return QVariant()

	def setData(self, index: T, value: typing.Any, role: int = Qt.DisplayRole) -> bool:
		model = index.model()
		if index.column() == 1:
			model[model.key(index)] = value
			return True
		else:
			old_key, key_value = model.key(index), model.value(index)
			new_last_key = value
			*parent_path, old_last_key = old_key.split(".")
			new_key = ".".join(parent_path + [new_last_key])
			del model[old_key]
			model[new_key] = key_value
			return True
