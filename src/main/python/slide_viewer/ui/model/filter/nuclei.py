from dataclasses import field, dataclass

from slide_viewer.common.dataclass_utils import dataclass_fields
from slide_viewer.ui.model.filter.base_filter import FilterData, FilterType


@dataclass(frozen=True)
class NucleiParams:
    foreground_threshold: int = 60
    min_radius: int = 10
    max_radius: int = 15
    local_max_search_radius: float = 10.0
    min_nucleus_area: int = 80


@dataclass_fields
class NucleiParams_(NucleiParams):
    pass


@dataclass(frozen=True)
class NucleiFilterData(FilterData):
    filter_type: FilterType = field(default=FilterType.NUCLEI, init=False)
    nuclei_params: NucleiParams = field(default_factory=NucleiParams)


@dataclass_fields
class NucleiFilterData_(NucleiFilterData):
    pass
