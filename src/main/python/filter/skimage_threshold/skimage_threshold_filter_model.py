from enum import unique, Enum
from typing import Any, ClassVar

from dataclasses import dataclass, field

# from filter.threshold_filter import ThresholdType
from filter.common.threshold_filter_model import ThresholdFilterData
from common.dataclass_utils import dataclass_fields


@unique
class SkimageThresholdType(str, Enum):
	threshold_mean = "threshold_mean"
	threshold_minimum = "threshold_minimum"


@dataclass(frozen=True)
class SkimageThresholdParams:
	type: SkimageThresholdType
	params: Any


@dataclass(frozen=True)
class SkimageMinimumThresholdParams:
	nbins: int = 256
	max_iter: int = 10000


@dataclass(frozen=True)
class SkimageThresholdFilterData(ThresholdFilterData):
	# filter_type: ClassVar[str] = 'skimage_threshold'
	filter_type: str =field(default='skimage_threshold')
	skimage_threshold_type: SkimageThresholdType = SkimageThresholdType.threshold_mean


@dataclass(frozen=True)
class SkimageMeanThresholdFilterData(SkimageThresholdFilterData):
	# skimage_threshold_type: SkimageThresholdType = field(default=SkimageThresholdType.threshold_mean, init=False)
	skimage_threshold_type: SkimageThresholdType = field(default=SkimageThresholdType.threshold_mean)


@dataclass(frozen=True)
class SkimageMinimumThresholdFilterData(SkimageThresholdFilterData):
	# skimage_threshold_type: SkimageThresholdType = field(default=SkimageThresholdType.threshold_minimum, init=False)
	skimage_threshold_type: SkimageThresholdType = field(default=SkimageThresholdType.threshold_minimum)
	skimage_threshold_minimum_params: SkimageMinimumThresholdParams = field(
		default_factory=SkimageMinimumThresholdParams)


@dataclass_fields
class SkimageMinimumThresholdParams_(SkimageMinimumThresholdParams):
	pass


@dataclass_fields
class SkimageMinimumThresholdParams_(SkimageMinimumThresholdParams):
	pass


@dataclass_fields
class SkimageThresholdFilterData_(SkimageThresholdFilterData):
	pass


@dataclass_fields
class SkimageMeanThresholdFilterData_(SkimageMeanThresholdFilterData):
	pass


@dataclass_fields
class SkimageMinimumThresholdFilterData_(SkimageMinimumThresholdFilterData):
	pass
