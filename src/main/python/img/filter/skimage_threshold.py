from enum import unique, Enum, auto
from typing import Any

from dataclasses import dataclass, field

from img.filter.threshold_filter import ThresholdFilterData, ThresholdType
from common.dataclass_utils import dataclass_fields


@unique
class SkimageThresholdType(str, Enum):
	threshold_mean = "threshold_mean"
	threshold_minimum = "threshold_minimum"
	# threshold_otsu = auto()
	# threshold_yen = auto()


@dataclass(frozen=True)
class SkimageThresholdParams:
	type: SkimageThresholdType
	params: Any


@dataclass(frozen=True)
class SkimageMinimumThresholdParams:
	nbins: int = 256
	max_iter: int = 10000


@dataclass_fields
class SkimageMinimumThresholdParams_(SkimageMinimumThresholdParams):
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
	skimage_threshold_minimum_params: SkimageMinimumThresholdParams = field(
		default_factory=SkimageMinimumThresholdParams)
	# nbins: int = 256
	# max_iter: int = 10000


@dataclass_fields
class SkimageMinimumThresholdFilterData_(SkimageMinimumThresholdFilterData):
	pass
