from collections import OrderedDict
from enum import Enum
from json.encoder import JSONEncoder
from typing import Any, Iterable, Type, TypeVar, Dict, Callable, Optional

import attr
from dataclasses import is_dataclass, asdict, fields, Field
from pydantic import BaseModel

from deepable.core import Deepable, is_deepable, isnamedtupleinstance, isnamedtupletype, deep_keys, deep_type_init_keys
from slide_viewer.ui.common.annotation_type import AnnotationType
from slide_viewer.ui.common.model import TreeViewConfig, AnnotationModel

JsonableByDefault = Any


class DeepableJSONEncoder(JSONEncoder):

	def default(self, obj: Any) -> JsonableByDefault:
		if is_deepable(obj):
			return deep_to_default(obj)
		elif isinstance(obj, Enum):
			# return obj.name
			return obj.value
		return super().default(obj)


def deep_to_dict(obj: Deepable) -> dict:
	if isinstance(obj, dict):
		return obj
	elif is_dataclass(obj):
		return asdict(obj)
	elif attr.has(type(obj)):
		return attr.asdict(obj)
	elif isinstance(obj, BaseModel):
		return obj.dict()
	elif isnamedtupleinstance(obj):
		return obj._asdict()
	else:
		raise ValueError(f"Cant convert object {obj} to dict")


def deep_to_default(obj: Deepable) -> JsonableByDefault:
	if is_dataclass(obj):
		return asdict(obj)
	elif attr.has(type(obj)):
		return attr.asdict(obj)
	elif isinstance(obj, BaseModel):
		return obj.dict()
	else:
		return obj


def common_object_pairs_hook(pairs: Iterable[tuple]):
	casted_pairs = []
	for key, value in pairs:
		if key == TreeViewConfig.snake_case_name:
			# casted_pairs.append((key, TreeViewConfig(**cast_dict(OrderedDict(value), TreeViewConfig)))) dataclass (only flat)
			# casted_pairs.append((key, TreeViewConfig(**value))) attrs (only flat)
			casted_pairs.append((key, TreeViewConfig.parse_obj(value)))  # pydantic (with nested objects!!!)
		elif key == 'annotation_type':
			casted_pairs.append((key, AnnotationType[value] if value else None))
		else:
			casted_pairs.append((key, value))
	return OrderedDict(casted_pairs)


D = TypeVar('D')


def type_for_key(type_: type, key: Any) -> Type:
	if attr.has(type_):
		field = next(filter(lambda f: f.name == key, attr.fields(type_)), None)
		return field.type if field else None
	elif issubclass(type_, BaseModel):
		field = next(filter(lambda f: f == key, type_.__fields__), None)
		return type_.__fields__[field].type_ if field else None
	elif is_dataclass(type_):
		field = next(filter(lambda f: f.name == key, fields(type_)), None)
		return field.type if field else None
	elif isnamedtupletype(type_):
		field = next(filter(lambda f: f == key, type_._fields), None)
		return type_._field_types[field] if field else None
	else:
		raise ValueError(f'type_for_key {type_} is not implemented')


def remove_extra_kwargs(d: dict, type_: type):
	keys = deep_type_init_keys(type_)
	return {k: d[k] for k in d if k in keys}


def kwargs_init_object_hook(dict_: dict, type_: Optional[type]):
	# print(f"dict {dict_} for type {type_}")
	if type_:
		cleared_kwargs = remove_extra_kwargs(dict_, type_)
		return type_(**cleared_kwargs)
	else:
		return dict_


# def deep_from_dict(d: dict, targetType: Type[D], factories: Dict[Type, Callable]) -> D:
def obj_from_dict(dict_: dict, object_hook: Callable[[dict, Optional[Type]], Any],
				  target_type: Optional[Type] = None) -> Any:
	if dict_ is None:
		return None
	new_items = []
	# TODO can use keys only for target_type
	for key, value in dict_.items():
		if isinstance(value, dict):
			value_target_type = type_for_key(target_type, key) if target_type else None
			obj = obj_from_dict(value, object_hook, value_target_type)
			new_items.append((key, obj))
		else:
			new_items.append((key, value))
	new_dict = dict(new_items)
	new_obj = object_hook(new_dict, target_type)
	return new_obj


def deep_from_dict(d: dict, target_type: Type):
	return obj_from_dict(d, kwargs_init_object_hook, target_type)
