from collections import OrderedDict
from enum import Enum
from json.encoder import JSONEncoder
from typing import Any, Iterable

import attr
from dataclasses import is_dataclass, asdict, fields, Field
from pydantic import BaseModel

from deepable.core import Deepable, is_deepable
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
