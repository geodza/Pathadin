import numpy as np
# noinspection PyUnresolvedReferences
import skimage.filters as filters

from common_image.core.threshold import ndarray_to_thresholded_ndarray, ndimg_to_thresholded_ndimg
from common_image.model.ndimg import Ndimg


def find_ndarray_skimage_threshold(ndarray: np.ndarray, filter_name: str = 'threshold_mean', **kwargs) -> float:
    threshold_func = getattr(filters, filter_name)
    threshold = threshold_func(ndarray, **kwargs)
    return threshold


def find_ndimg_skimage_threshold(ndimg: Ndimg, filter_name: str = 'threshold_mean', **kwargs) -> float:
    foreground_color_points = ndimg.ndarray[ndimg.bool_mask_ndarray] if ndimg.bool_mask_ndarray is not None else ndimg.ndarray
    threshold = find_ndarray_skimage_threshold(foreground_color_points, filter_name, **kwargs)
    return threshold


def ndarray_to_skimage_thresholded_ndarray(ndarray: np.ndarray, filter_name: str = 'threshold_mean', **kwargs) -> np.ndarray:
    threshold = find_ndarray_skimage_threshold(ndarray, filter_name, **kwargs)
    threshold_range = (0, int(threshold))
    return ndarray_to_thresholded_ndarray(ndarray, threshold_range)


def ndimg_to_skimage_thresholded_ndimg(ndimg: Ndimg, filter_name: str = 'threshold_mean', **kwargs) -> Ndimg:
    threshold = find_ndimg_skimage_threshold(ndimg, filter_name, **kwargs)
    threshold_range = (0, int(threshold))
    return ndimg_to_thresholded_ndimg(ndimg, threshold_range)
