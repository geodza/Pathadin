from typing import Tuple

import histomicstk.segmentation.positive_pixel_count as ppc
import skimage.color
import skimage.util
from dataclasses import field, dataclass, asdict

from common.dataclass_utils import dataclass_fields
from common_image.model.ndimg import Ndimg
from img.filter.base_filter import FilterData, FilterType, FilterResults2


@dataclass(frozen=True)
class PositivePixelCountParams():
    # params: ppc.Parameters = default_ppc_params()
    hue_value: float = 0.05
    hue_width: float = 0.15
    saturation_minimum: float = 0.05
    intensity_upper_limit: float = 0.95
    intensity_weak_threshold: float = 0.65
    intensity_strong_threshold: float = 0.35
    intensity_lower_limit: float = 0.05


def positive_pixel_count2(img: Ndimg, params: PositivePixelCountParams) -> Tuple[Ndimg, ppc.Output]:
    stats, label_image = ppc.count_image(img.ndarray, ppc.Parameters(**asdict(params)))
    colors = [(0, 0, 0), (0.5, 0.5, 0.5), (0.75, 0.75, 0.75), (1, 1, 1)]
    labeled_ndimg = skimage.color.label2rgb(label_image, colors=colors, bg_label=0)
    labeled_ndimg = skimage.util.img_as_ubyte(labeled_ndimg, force_copy=True)
    return (Ndimg(labeled_ndimg, "RGB", img.bool_mask_ndarray), stats)


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
