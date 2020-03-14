import typing
from enum import unique, Enum, auto

from dataclasses import dataclass, field

from common.dataclass_utils import dataclass_fields
from img.filter.base_filter import FilterData, FilterType, FilterResults2

HSV = typing.Tuple[int, int, int]


@unique
class ThresholdType(Enum):
    MANUAL = auto()
    SKIMAGE_AUTO = auto()


# https://scikit-image.org/docs/dev/api/skimage.filters.html


@dataclass(frozen=True)
class ThresholdFilterData(FilterData):
    filter_type: FilterType = field(default=FilterType.THRESHOLD, init=False)
    threshold_type: ThresholdType = field(init=False)


@dataclass_fields
class ThresholdFilterData_(ThresholdFilterData):
    pass


@dataclass
class ThresholdFilterResults(FilterResults2):
    histogram_html: str