import collections
import typing
import attr
from dataclasses import fields, is_dataclass, dataclass
from pydantic import BaseModel

from typing import Any, Union, List, Dict, Set, Optional

DataClass = Any
Deepable = Union[dict, DataClass]


def isnamedtupleinstance(x):
	t = type(x)
	# b = t.__bases__
	# if len(b) != 1 or b[0] != tuple: return False
	f = getattr(t, '_fields', None)
	if not isinstance(f, tuple): return False
	return all(type(n) == str for n in f)


# def _len(obj):
#     if isinstance()

def is_deepable(obj) -> bool:
	return isinstance(obj, dict) or is_dataclass(obj) or attr.has(type(obj)) or isinstance(obj, BaseModel) \
		   or isnamedtupleinstance(obj) or isinstance(obj, (list, tuple))


def deep_get(obj: Deepable, key: str) -> Any:
	keys = key.split('.')
	child_obj = obj
	for child_key in keys:
		if isinstance(child_obj, dict):
			try:
				dict_type = type(child_obj)
				child_obj = dict_type.__getitem__(child_obj, child_key)
			# TODO return None or throw?
			# child_obj = child_obj.get(child_key, None)
			except KeyError as e:
				print(e)
				raise e
		# return None
		elif isinstance(child_obj, (list, tuple)):
			try:
				child_obj = child_obj[int(child_key)]
			except IndexError as e:
				print(e)
				raise e
		else:
			try:
				child_obj = getattr(child_obj, child_key)
			except AttributeError as e:
				print(e)
				raise e
	# return None
	return child_obj


# def deep_get_default(obj: Deepable, key: str, default=None) -> Any:
# 	keys = key.split('.')
# 	child_obj = obj
# 	for child_key in keys:
# 		if isinstance(child_obj, dict):
# 			try:
# 				dict_type = type(child_obj)
# 				child_obj = dict_type.__getitem__(child_obj, child_key)
# 			# TODO return None or throw?
# 			# child_obj = child_obj.get(child_key, None)
# 			except KeyError as e:
# 				return default
# 		# return None
# 		else:
# 			try:
# 				child_obj = getattr(child_obj, child_key)
# 			except AttributeError as e:
# 				return default
# 	# return None
# 	return child_obj


def deep_set(obj: Deepable, key: str, value: Any) -> None:
	*leading_keys, last_key = key.split('.')
	child_obj = deep_get(obj, '.'.join(leading_keys)) if leading_keys else obj
	if isinstance(child_obj, dict):
		dict_type = type(child_obj)
		dict_type.__setitem__(child_obj, last_key, value)
	elif isinstance(child_obj, (list, tuple)):
		try:
			child_obj.__setitem__(int(last_key), value)
		except IndexError:
			child_obj.insert(int(last_key), value)
	# child_obj[int(last_key)] = value
	else:
		setattr(child_obj, last_key, value)


def deep_del(obj: Deepable, key: str) -> None:
	*leading_keys, last_key = key.split('.')
	child_obj = deep_get(obj, '.'.join(leading_keys)) if leading_keys else obj
	if isinstance(child_obj, dict):
		dict_type = type(child_obj)
		dict_type.__delitem__(child_obj, last_key)
	elif isinstance(child_obj, (list, tuple)):
		del child_obj[int(last_key)]
	else:
		delattr(child_obj, last_key)


def deep_keys(obj: Deepable) -> list:
	if isinstance(obj, dict):
		return list(obj.keys())
	# if isinstance(obj, typing.Dict):
	#     return list(obj.keys())
	elif isinstance(obj, (list, tuple)):
		return [str(i) for i in range(len(obj))]
	elif attr.has(type(obj)):
		return [f.name for f in attr.fields(type(obj))]
	elif isinstance(obj, BaseModel):
		return [name for name in obj.__fields__]
	elif is_dataclass(obj):
		return [f.name for f in fields(obj)]
	elif isnamedtupleinstance(obj):
		return list(obj._fields)
	else:
		raise ValueError(f'object {obj} is not Deepable')


def deep_contains(obj: Deepable, key: str) -> bool:
	return key in deep_keys_deep(obj)


def deep_iter(obj: Deepable) -> typing.Iterator:
	return iter(deep_keys(obj))


def deep_len(obj: Deepable) -> int:
	return len(deep_keys(obj))


def deep_local_path(key: str) -> List[str]:
	return key.split('.', 1)[1:]


def deep_local_key(key: str) -> str:
	return key.split('.')[-1]


def deep_key_index(obj: Deepable, key: str) -> int:
	*parent_path, child_key = key.split('.')
	parent_key = '.'.join(parent_path)
	parent_object: Deepable = deep_get(obj, parent_key) if parent_key else obj
	key_index = deep_keys(parent_object).index(child_key)
	return key_index


def deep_index_key(obj: Deepable, index: int) -> str:
	keys = list(deep_keys(obj))
	key = keys[index]
	return key


def deep_new_key_index(obj: Deepable, key: str) -> int:
	*parent_path, child_key = key.split('.')
	parent_key = '.'.join(parent_path)
	parent_object: Deepable = deep_get(obj, parent_key) if parent_key else obj
	if isinstance(parent_object, dict):
		return len(parent_object)
	elif isinstance(parent_object, (list,)):
		return len(parent_object)
	else:
		raise ValueError(f"Deepable object of type: {type(parent_object)} doesnt support new keys")


def deep_supports_key_add(obj: Deepable) -> bool:
	if isinstance(obj, dict):
		return True
	elif isinstance(obj, (list,)):
		return True
	else:
		return False


def deep_supports_key_delete(obj: Deepable) -> bool:
	if isinstance(obj, dict):
		return True
	else:
		return False


def deep_keys_deep(obj: Deepable) -> list:
	keys = deep_keys(obj)
	keys_ = []
	for key in keys:
		value = deep_get(obj, key)
		if is_deepable(value) and not is_immutable(value):
			value_keys = deep_keys_deep(value)
			obj_value_keys = [".".join([key, value_key]) for value_key in value_keys]
			keys_.extend(obj_value_keys)
		else:
			keys_.append(key)
	return keys_


def deep_items(obj: Deepable) -> list:
	return [(key, deep_get(obj, key)) for key in deep_keys(obj)]


def toplevel_key(key: str) -> str:
	return key.split('.')[0]


def toplevel_keys(keys: typing.List[str]) -> typing.Set[str]:
	return set(toplevel_key(k) for k in keys)


@dataclass
class DeepDiffChange:
	old_value: Optional[Any]
	new_value: Optional[Any]


@dataclass
class DeepDiffChanges:
	removed: Set[str]
	added: Dict[str, Optional[Any]]
	changed: Dict[str, DeepDiffChange]


def deep_diff(obj1: Optional[Deepable], obj2: Optional[Deepable]) -> DeepDiffChanges:
	# if is_immutable(obj1) and is_immutable(obj2) and obj1!=
	keys1 = set(deep_keys_deep(obj1)) if obj1 else set()
	keys2 = set(deep_keys_deep(obj2)) if obj2 else set()
	keys1_only = keys1 - keys2
	keys2_only = keys2 - keys1
	keys_both = keys1.intersection(keys2)
	added = {}
	for key in keys2_only:
		added_value = deep_get(obj2, key)
		added[key] = added_value
	changes = {}
	for key in keys_both:
		value1 = deep_get(obj1, key)
		value2 = deep_get(obj2, key)
		if value1 != value2:
			# comparing by eq means we capture diff only for immutable objects
			changes[key] = DeepDiffChange(old_value=value1, new_value=value2)
	return DeepDiffChanges(keys1_only, added, changes)


def is_immutable(obj: Any) -> bool:
	return isinstance(obj, collections.Hashable)
# return hasattr(obj, "__hash__")

# if (hasattr(old_value, "__hash__") or hasattr(value, "__hash__")) and old_value!=value:


# def deep_diff2(obj1: Deepable, obj2: Deepable) -> dict:
# 	keys1 = set(deep_keys(obj1))
# 	keys2 = set(deep_keys(obj2))
# 	keys1_only = keys1 - keys2
# 	keys2_only = keys2 - keys1
# 	keys_both = keys1.intersection(keys2)
# 	changes = {}
# 	if keys1_only:
# 		changes["removed"] = keys1_only
# 	if keys2_only:
# 		changes["added"] = keys2_only
# 	changes["changed"] = {}
# 	for key in keys_both:
# 		value1 = deep_get(obj1, key)
# 		value2 = deep_get(obj2, key)
# 		if is_deepable(value1) and is_deepable(value2):
# 			diff2 = deep_diff(value1, value2)
# 			changes["changed"][key] = diff2
# 		elif value1 != value2:
# 			changes["changed"][key] = {"old": value1, "new": value2}
# 		#
# 		if not changes["changed"][key]:
# 			del changes["changed"][key]
# 	# comparing by eq means we capture diff only for immutable objects
# 	if not changes["changed"]:
# 		del changes["changed"]
# 	return changes
#


# @singledispatch
# def default(val):
#     return val

#
# @default.register(Enum)
# def f(e: Enum):
#     return e.name
