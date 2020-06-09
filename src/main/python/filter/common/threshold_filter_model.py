from dataclasses import dataclass

from common.dataclass_utils import dataclass_fields
from filter.common.filter_model import FilterData


@dataclass(frozen=True)
class ThresholdFilterData(FilterData):
	realtime: bool = True


@dataclass_fields
class ThresholdFilterData_(ThresholdFilterData):
	pass
