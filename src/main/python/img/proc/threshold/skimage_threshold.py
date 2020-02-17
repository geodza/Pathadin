import numpy as np
from dataclasses import asdict

from img.filter.skimage_threshold import SkimageAutoThresholdFilterData, SkimageMeanThresholdFilterData, \
    SkimageMinimumThresholdFilterData, SkimageMinimumThresholdFilterData_, SkimageThresholdParams, SkimageThresholdType
from common_image.model.ndimg import Ndimg
from common.dict_utils import remove_none_values, narrow_dict


# @gcached("skimage_threshold")
def skimage_threshold(img: np.ndarray, filter_data: SkimageAutoThresholdFilterData) -> float:
    if isinstance(filter_data, SkimageMeanThresholdFilterData):
        from skimage.filters import threshold_mean
        return threshold_mean(img)
    elif isinstance(filter_data, SkimageMinimumThresholdFilterData):
        from skimage.filters import threshold_minimum
        kwargs = remove_none_values(narrow_dict(asdict(filter_data),
                                                [SkimageMinimumThresholdFilterData_.nbins,
                                                 SkimageMinimumThresholdFilterData_.max_iter]))
        return threshold_minimum(img, **kwargs)


def ndimg_to_skimage_threshold_range(params: SkimageThresholdParams, img: Ndimg) -> tuple:
    foreground_color_points = img.ndarray[img.bool_mask_ndarray] if img.bool_mask_ndarray is not None else img.ndarray
    if params.type == SkimageThresholdType.threshold_mean:
        from skimage.filters import threshold_mean
        res = threshold_mean(foreground_color_points)
        return (int(res), 255)
    elif params.type == SkimageThresholdType.threshold_minimum:
        from skimage.filters import threshold_minimum
        kwargs = remove_none_values(asdict(params.params))
        res = threshold_minimum(foreground_color_points, **kwargs)
        return (int(res), 255)
    else:
        raise ValueError()
