from dataclasses import field, dataclass

from img.proc.keras_model import KerasModelParams
from slide_viewer.common.dataclass_utils import dataclass_fields
from img.filter.base_filter import FilterData, FilterType, FilterResults2


@dataclass(frozen=True)
class KerasModelFilterData(FilterData):
    filter_type: FilterType = field(default=FilterType.KERAS_MODEL, init=False)
    keras_model_params: KerasModelParams = field(default_factory=KerasModelParams)


@dataclass_fields
class KerasModelFilterData_(KerasModelFilterData):
    pass


@dataclass
class KerasModelFilterResults(FilterResults2):
    pass
