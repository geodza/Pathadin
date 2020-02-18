from typing import Tuple

import cv2
import numpy as np

from common_image.model.ndimg import Ndimg


def ndarray_to_thresholded_ndarray(ndarray: np.ndarray, threshold_range: Tuple) -> np.ndarray:
    ranges = np.array(threshold_range, dtype=np.uint8)
    ranges = ranges.reshape((2, -1))
    lower, upper = ranges[0], ranges[1]
    outer = ranges[0] > ranges[1]
    if not np.any(outer):
        result_ndarray = cv2.inRange(ndarray, ranges[0], ranges[1])
    else:
        result_ndarray = np.copy(ndarray)
        nchannels = len(lower)
        for channel in range(nchannels):
            l, u = (lower, upper) if lower[channel] <= upper[channel] else (upper, lower)
            result_ndarray[..., channel] = cv2.inRange(result_ndarray[..., channel], l[channel, np.newaxis], u[channel, np.newaxis])
            if lower[channel] > upper[channel]:
                result_ndarray[..., channel] = cv2.bitwise_not(result_ndarray[..., channel])
        result_ndarray = np.sum(result_ndarray != 0, axis=2, dtype=np.uint8)
        result_ndarray[:] = result_ndarray // nchannels
        result_ndarray[:] = result_ndarray * 255
    result_ndarray = np.atleast_3d(result_ndarray)
    return result_ndarray


def ndimg_to_thresholded_ndimg(ndimg: Ndimg, threshold_range: Tuple) -> Ndimg:
    thresholded_ndarray = ndarray_to_thresholded_ndarray(ndimg.ndarray, threshold_range)
    return Ndimg(thresholded_ndarray, "L", ndimg.bool_mask_ndarray)
