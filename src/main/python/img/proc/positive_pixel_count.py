from typing import Tuple

import histomicstk.segmentation.positive_pixel_count as ppc
import skimage.color
from dataclasses import dataclass, asdict

from common_image.model.ndimagedata import NdImageData

colors = [(0, 0, 0), (0.5, 0.5, 0.5), (0.75, 0.75, 0.75), (1, 1, 1)]


# def default_ppc_params() -> ppc.Parameters:
#     return ppc.Parameters(hue_value=0.05,
#                           hue_width=0.15,
#                           saturation_minimum=0.05,
#                           intensity_upper_limit=0.95,
#                           intensity_weak_threshold=0.65,
#                           intensity_strong_threshold=0.35,
#                           intensity_lower_limit=0.05)


# print(isnamedtupleinstance(default_ppc_params()))


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


# print(PositivePixelCountParams.params)


def positive_pixel_count2(img: NdImageData, params: PositivePixelCountParams) -> Tuple[NdImageData, ppc.Output]:
    stats, label_image = ppc.count_image(img.ndimg, ppc.Parameters(**asdict(params)))
    labeled_ndimg = skimage.color.label2rgb(label_image, colors=colors, bg_label=0)
    labeled_ndimg = skimage.util.img_as_ubyte(labeled_ndimg, force_copy=True)
    return (NdImageData(labeled_ndimg, "RGB", img.bool_mask_ndimg), stats)
