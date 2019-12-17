import typing
from collections import OrderedDict
from enum import Enum
from json import JSONEncoder
from typing import Any, Union, Iterable

import attr
from dataclasses import fields, is_dataclass, asdict, Field
from pydantic import BaseModel

from slide_viewer.ui.model.annotation_type import AnnotationType
from slide_viewer.ui.odict.deep.model import TreeViewConfig

DataClass = Any
Deepable = Union[OrderedDict, DataClass]


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
    return isinstance(obj, OrderedDict) or is_dataclass(obj) or attr.has(type(obj)) or isinstance(obj, BaseModel) \
           or isnamedtupleinstance(obj)


def deep_get(obj: Deepable, key: str) -> Any:
    keys = key.split('.')
    child_obj = obj
    for child_key in keys:
        if isinstance(child_obj, OrderedDict):
            try:
                child_obj = OrderedDict.__getitem__(child_obj, child_key)
                # TODO return None or throw?
                # child_obj = child_obj.get(child_key, None)
            except KeyError as e:
                # print(e)
                return None
        else:
            try:
                child_obj = getattr(child_obj, child_key)
            except AttributeError as e:
                return None
    return child_obj


def deep_set(obj: Deepable, key: str, value: Any) -> None:
    *leading_keys, last_key = key.split('.')
    child_obj = deep_get(obj, '.'.join(leading_keys)) if leading_keys else obj
    if isinstance(child_obj, OrderedDict):
        OrderedDict.__setitem__(child_obj, last_key, value)
    else:
        setattr(child_obj, last_key, value)


def deep_del(obj: Deepable, key: str) -> None:
    *leading_keys, last_key = key.split('.')
    child_obj = deep_get(obj, '.'.join(leading_keys)) if leading_keys else obj
    if isinstance(child_obj, OrderedDict):
        OrderedDict.__delitem__(child_obj, last_key)
    else:
        delattr(child_obj, last_key)


def deep_keys(obj: Deepable) -> list:
    if isinstance(obj, OrderedDict):
        return list(obj.keys())
    # if isinstance(obj, typing.Dict):
    #     return list(obj.keys())
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


def deep_items(obj: Deepable) -> list:
    return [(key, deep_get(obj, key)) for key in deep_keys(obj)]


def toplevel_key(key: str) -> str:
    return key.split('.')[0]


def toplevel_keys(keys: typing.List[str]) -> typing.Set[str]:
    return set(toplevel_key(k) for k in keys)


# @singledispatch
# def default(val):
#     return val

#
# @default.register(Enum)
# def f(e: Enum):
#     return e.name


class CommonJSONEncoder(JSONEncoder):

    def default(self, o):
        if is_dataclass(o):
            return asdict(o)
        elif attr.has(type(o)):
            return attr.asdict(o)
        elif isinstance(o, BaseModel):
            return o.dict()
        elif isinstance(o, Enum):
            return o.name
        return super().default(o)


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


def cast_dict(dict_: dict, cls: type) -> OrderedDict:
    # name_to_field: Mapping[str, Field] = OrderedDict([(f.name, f) for f in fields(cls)])
    casted = OrderedDict()
    for field_ in fields(cls):
        field: Field = field_
        value = dict_.get(field.name, field.default)
        if issubclass(field.type, Enum):
            casted[field.name] = field.type[value]
        else:
            casted[field.name] = field.type(value)
    return casted
