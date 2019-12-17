from dataclasses import field, dataclass

from img.proc.nuclei import NucleiParams
from img.proc.positive_pixel_count import PositivePixelCountParams
from slide_viewer.common.dataclass_utils import dataclass_fields
from img.filter.base_filter import FilterData, FilterType, FilterResults2
import histomicstk.segmentation.positive_pixel_count as ppc


@dataclass(frozen=True)
class PositivePixelCountFilterData(FilterData):
    filter_type: FilterType = field(default=FilterType.POSITIVE_PIXEL_COUNT, init=False)
    positive_pixel_count_params: PositivePixelCountParams = field(default_factory=PositivePixelCountParams)


@dataclass_fields
class PositivePixelCountFilterData_(PositivePixelCountFilterData):
    pass


@dataclass
class PositivePixelCountFilterResults(FilterResults2):
    stats: ppc.Output