from typing import Optional

from dataclasses import field, dataclass

from common.dataclass_utils import dataclass_fields
from filter.common.filter_data import FilterData

KERAS_MODEL_PARAMS_DEFAULT_COLOR_TUPLE_PATTERN = "(0, 255, 0, 'y')"
KERAS_MODEL_PARAMS_DEFAULT_MULTICLASS_CMAP = 'viridis'
KERAS_MODEL_PARAMS_DEFAULT_CMAP = KERAS_MODEL_PARAMS_DEFAULT_COLOR_TUPLE_PATTERN


@dataclass(frozen=True)
class KerasModelParams:
	model_path: Optional[str] = None
	alpha_scale: float = 0.5
	invert: bool = False
	scale_image: bool = True
	patch_size_scale: float = 1.0
	cmap: str = KERAS_MODEL_PARAMS_DEFAULT_CMAP


@dataclass_fields
class KerasModelParams_(KerasModelParams):
	pass


@dataclass(frozen=True)
class KerasModelFilterData(FilterData):
	# filter_type: FilterType = field(default=FilterType.KERAS_MODEL, init=False)
	# filter_type: ClassVar[str] = "keras_model"
	keras_model_params: KerasModelParams = field(default_factory=KerasModelParams)
	filter_type: str = field(default='keras_model')


@dataclass_fields
class KerasModelFilterData_(KerasModelFilterData):
	pass
