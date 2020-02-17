import typing

from dataclasses import dataclass, field

from common_image.model.color_mode import ColorMode
from img.filter.threshold_filter import ThresholdFilterData, ThresholdType, HSV
from common.dataclass_utils import dataclass_fields


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