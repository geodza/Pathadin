from typing import Tuple

import cv2
import numpy as np

from common_image.ndimagedata import NdImageData


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
    return result_ndarray


def ndimg_to_thresholded_ndimg(ndimg: NdImageData, threshold_range: Tuple) -> NdImageData:
    thresholded_ndarray = ndarray_to_thresholded_ndarray(ndimg.ndimg, threshold_range)
    return NdImageData(thresholded_ndarray, "L", ndimg.bool_mask_ndimg)


if __name__ == '__main__':
    a = np.arange(255 * 2 * 4 * 3).reshape((255, 2, 4, 3))
    np.transpose(a, axes=(0, 2, 3, 1))[..., 0, :] = [20, 60]
    print(a[:, 0, :, :])

    ndimg = NdImageData(np.array([[
        [160, 40, 50],
        [20, 40, 50],
        [50, 40, 50]
    ]
    ], dtype=np.uint8), 'HSV')
    # j=np.take(ndimg.ndimg, [[0,2],[0,2],])
    j = ndimg.ndimg[[0], [1], :]
    i = ndimg.ndimg[:, :, [1]]
    thres = ((150, 30, 40), (30, 50, 60))
    res = ndimg_to_thresholded_ndimg(ndimg, thres)
    a = np.array((50, 100))
    b = np.array(((10, 20, 30), (40, 50, 10)))
    c = b[0] > b[1]
    bc = np.copy(b)
    bc[0, c] = 0
    bc[1, c] = 255
    print(a, b, c)
