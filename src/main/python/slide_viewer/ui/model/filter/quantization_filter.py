from enum import unique, IntEnum

from PIL.Image import Image
from dataclasses import dataclass, field

from slide_viewer.common.dataclass_utils import dataclass_fields
from slide_viewer.ui.common.common import get_default_arg
from slide_viewer.ui.model.filter.base_filter import FilterData, FilterType


@unique
# https://pillow.readthedocs.io/en/stable/reference/Image.html#PIL.Image.Image.quantize
class PillowQuantizeMethod(IntEnum):
    # median_cut = 0
    # maximum_coverage = 1
    fast_octree = 2
    # libimagequant = 3


@dataclass(frozen=True)
class QuantizationFilterData(FilterData):
    filter_type: FilterType = field(default=FilterType.QUANTIZATION, init=False)
    colors: int = get_default_arg(Image.quantize, 'colors')
    method: PillowQuantizeMethod = PillowQuantizeMethod.fast_octree


@dataclass_fields
class QuantizationFilterData_(QuantizationFilterData):
    pass