from dataclasses import field, dataclass

from img.proc.nuclei import NucleiParams
from slide_viewer.common.dataclass_utils import dataclass_fields
from img.filter.base_filter import FilterData, FilterType, FilterResults2


# @dataclass(frozen=True)
# class NucleiParams:
#     foreground_threshold: int = 60
#     min_radius: int = 10
#     max_radius: int = 15
#     local_max_search_radius: float = 10.0
#     min_nucleus_area: int = 80
#
#
# @dataclass_fields
# class NucleiParams_(NucleiParams):
#     pass


@dataclass(frozen=True)
class NucleiFilterData(FilterData):
    filter_type: FilterType = field(default=FilterType.NUCLEI, init=False)
    nuclei_params: NucleiParams = field(default_factory=NucleiParams)


@dataclass_fields
class NucleiFilterData_(NucleiFilterData):
    pass


@dataclass
class NucleiFilterResults(FilterResults2):
    nuclei_count: int