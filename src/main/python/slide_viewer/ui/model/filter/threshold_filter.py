import typing
from enum import unique, Enum, auto

from dataclasses import dataclass, field

from slide_viewer.common.dataclass_utils import dataclass_fields
from slide_viewer.ui.model.color_mode import ColorMode
from slide_viewer.ui.model.filter.base_filter import FilterData, FilterType

HSV = typing.Tuple[int, int, int]


@unique
class ThresholdType(Enum):
    MANUAL = auto()
    SKIMAGE_AUTO = auto()


# https://scikit-image.org/docs/dev/api/skimage.filters.html
@unique
class SkimageThresholdType(Enum):
    threshold_mean = auto()
    threshold_minimum = auto()
    threshold_otsu = auto()
    threshold_yen = auto()


@dataclass(frozen=True)
class ThresholdFilterData(FilterData):
    filter_type: FilterType = field(default=FilterType.THRESHOLD, init=False)
    threshold_type: ThresholdType = field(init=False)


@dataclass_fields
class ThresholdFilterData_(ThresholdFilterData):
    pass


@dataclass(frozen=True)
class ManualThresholdFilterData(ThresholdFilterData):
    threshold_type: ThresholdType = field(default=ThresholdType.MANUAL, init=False)
    color_mode: ColorMode = field(init=False)


@dataclass_fields
class ManualThresholdFilterData_(ManualThresholdFilterData):
    pass


@dataclass(frozen=True)
class GrayManualThresholdFilterData(ManualThresholdFilterData):
    color_mode: ColorMode = field(default=ColorMode.L, init=False)
    gray_range: typing.Tuple[int, int] = (0, 255)


@dataclass_fields
class GrayManualThresholdFilterData_(GrayManualThresholdFilterData):
    pass


@dataclass(frozen=True)
class HSVManualThresholdFilterData(ManualThresholdFilterData):
    color_mode: ColorMode = field(default=ColorMode.HSV, init=False)
    hsv_range: typing.Tuple[HSV, HSV] = ((0, 0, 0), (255, 255, 255))


@dataclass_fields
class HSVManualThresholdFilterData_(HSVManualThresholdFilterData):
    pass


@dataclass(frozen=True)
class SkimageAutoThresholdFilterData(ThresholdFilterData):
    threshold_type: ThresholdType = field(default=ThresholdType.SKIMAGE_AUTO, init=False)
    skimage_threshold_type: SkimageThresholdType = SkimageThresholdType.threshold_mean
    # skimage_threshold_type: SkimageThresholdType = field(init=False)
    # method: str
    # args: typing.Optional[list]
    # kwargs: typing.Optional[dict]


@dataclass_fields
class SkimageAutoThresholdFilterData_(SkimageAutoThresholdFilterData):
    pass


@dataclass(frozen=True)
class SkimageMeanThresholdFilterData(SkimageAutoThresholdFilterData):
    skimage_threshold_type: SkimageThresholdType = field(default=SkimageThresholdType.threshold_mean, init=False)


@dataclass_fields
class SkimageMeanThresholdFilterData_(SkimageMeanThresholdFilterData):
    pass


@dataclass(frozen=True)
class SkimageMinimumThresholdFilterData(SkimageAutoThresholdFilterData):
    skimage_threshold_type: SkimageThresholdType = field(default=SkimageThresholdType.threshold_minimum, init=False)
    nbins: int = 256
    max_iter: int = 10000


@dataclass_fields
class SkimageMinimumThresholdFilterData_(SkimageMinimumThresholdFilterData):
    pass
