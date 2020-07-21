from typing import Optional, ClassVar

from dataclasses import field, dataclass

from common.dataclass_utils import dataclass_fields
from filter.common.filter_output import FilterOutput
from filter.common.filter_data import FilterData


@dataclass(frozen=True)
class KerasModelParams:
	model_path: Optional[str] = None
	alpha_scale: float = 0.5
	invert: bool = False


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
