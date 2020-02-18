from dataclasses import field, dataclass

from common.dataclass_utils import dataclass_fields
from common_image.model.ndimg import Ndimg
from img.filter.base_filter import FilterData, FilterType, FilterResults2


@dataclass(frozen=True)
class KerasModelParams():
    model_path: str


@dataclass_fields
class KerasModelParams_(KerasModelParams):
    pass


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


@dataclass
class KerasModelResults:
    labeled_img: Ndimg
    region_props: list
