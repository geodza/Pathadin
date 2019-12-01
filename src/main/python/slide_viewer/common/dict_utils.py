from collections import OrderedDict
from typing import Collection, TypeVar, Type, Dict

from dataclasses import fields, is_dataclass

K = TypeVar('K')
V = TypeVar('V')
T = TypeVar('T')


def narrow_dict(dict_: Dict[K, V], keys_to_retain: Collection[K]) -> Dict[K, V]:
    return OrderedDict({k: v for k, v in dict_.items() if k in keys_to_retain})


def narrow_dict_to_data_dict(dict_: Dict[K, V], data_type: Type[T]) -> Dict[K, V]:
    data_dict = OrderedDict()
    for f in fields(data_type):
        if f.init and f.name in dict_:
            v = dict_[f.name]
            if is_dataclass(f.type) and not is_dataclass(v):
                v = narrow_dict_to_data_dict(v, f.type)
            data_dict[f.name] = v
    # keys_to_retain = [f.name for f in fields(data_type) if f.init]
    # data_dict = narrow_dict(dict_, keys_to_retain)
    return data_dict


def asodict(data) -> OrderedDict:
    data_dict = OrderedDict()
    for f in fields(data):
        v = getattr(data, f.name)
        if is_dataclass(f.type):
            v = asodict(v)
        data_dict[f.name] = v
    return data_dict


def dict_to_data_ignore_extra(dict_: Dict[K, V], data_type: Type[T]) -> T:
    # data_dict = narrow_dict_to_data_dict(dict_, data_type)
    # data_type_val = data_type(**data_dict)
    # return data_type_val
    data_dict = narrow_dict_to_data_dict(dict_, data_type)
    for f in fields(data_type):
        if f.init and f.name in dict_:
            v = dict_[f.name]
            if is_dataclass(f.type) and not is_dataclass(v):
                v = dict_to_data_ignore_extra(v, f.type)
            data_dict[f.name] = v
    data_type_val = data_type(**data_dict)
    return data_type_val


def remove_none_values(dict_: Dict[K, V]) -> Dict[K, V]:
    return {k: v for k, v in dict_.items() if v is not None}
