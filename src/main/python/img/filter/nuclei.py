from dataclasses import field, dataclass

from common_image.model.ndimg import Ndimg
from common.dataclass_utils import dataclass_fields
from img.filter.base_filter import FilterData, FilterType, FilterResults2


@dataclass(frozen=True)
class NucleiParams():
    # stain_color_map: Dict[str, list] = field(default_factory=default_stain_color_map)  # specify stains of input image
    stain_1: str = 'hematoxylin'  # nuclei stain
    stain_2: str = 'eosin'  # cytoplasm stain
    stain_3: str = 'null'  # set to null of input contains only two stains
    foreground_threshold: int = 60
    min_radius: int = 10
    max_radius: int = 15
    local_max_search_radius: float = 10.0
    min_nucleus_area: int = 80


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


def default_stain_color_map():
    return {
        'hematoxylin': [0.65, 0.70, 0.29],
        'eosin': [0.07, 0.99, 0.11],
        'dab': [0.27, 0.57, 0.78],
        'null': [0.0, 0.0, 0.0]
    }

