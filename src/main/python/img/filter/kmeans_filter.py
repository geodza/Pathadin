from dataclasses import dataclass, field

from img.proc.kmeans import KMeansParams
from common.dataclass_utils import dataclass_fields
from img.filter.base_filter import FilterData, FilterType, FilterResults2


@dataclass(frozen=True)
class KMeansFilterData(FilterData):
    filter_type: FilterType = field(default=FilterType.KMEANS, init=False)
    kmeans_params: KMeansParams = field(default_factory=KMeansParams)


@dataclass_fields
class KMeansFilterData_(KMeansFilterData):
    pass


@dataclass
class KMeansFilterResults(FilterResults2):
    histogram_html: str