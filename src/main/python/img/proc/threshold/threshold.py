from typing import Tuple

import cv2
import numpy as np

from img.ndimagedata import NdImageData


def ndimg_to_thresholded_ndimg(threshold_range: Tuple, i: NdImageData) -> NdImageData:
    lower, upper = np.array(threshold_range[0]), np.array(threshold_range[1])
    # inner=lower<=upper
    # outer=lower>upper
    ranges = np.array(threshold_range, dtype=np.uint8)
    ranges = ranges.reshape((2, -1))
    lower, upper = ranges[0], ranges[1]
    outer = ranges[0] > ranges[1]
    if not np.any(outer):
        result_ndimg = cv2.inRange(i.ndimg, ranges[0], ranges[1])
    else:
        result_ndimg = np.copy(i.ndimg)
        nchannels = len(lower)
        for channel in range(nchannels):
            l, u = (lower, upper) if lower[channel] <= upper[channel] else (upper, lower)
            result_ndimg[..., channel] = cv2.inRange(result_ndimg[..., channel], l[channel, np.newaxis], u[channel, np.newaxis])
            result_ndimg = np.atleast_3d(result_ndimg)
            if lower[channel] > upper[channel]:
                # result_ndimg[..., channel]=(result_ndimg[..., channel]!=0)
                result_ndimg[..., channel] = cv2.bitwise_not(result_ndimg[..., channel])
                result_ndimg = np.atleast_3d(result_ndimg)
                # cv2.bitwise_and(result_ndimg[..., channel], result_ndimg[..., channel])
        result_ndimg = np.sum(result_ndimg != 0, axis=2, dtype=np.uint8)
        result_ndimg[:] = result_ndimg // nchannels
        result_ndimg[:] = result_ndimg * 255

        # ranges_inner = np.copy(ranges)
        # ranges_inner[0, outer] = 0
        # ranges_inner[1, outer] = ranges[1][outer]
        # result_ndimg1 = cv2.inRange(i.ndimg, ranges_inner[0], ranges_inner[1])
        # ranges_inner[0, outer] = ranges[0][outer]
        # ranges_inner[1, outer] = 255
        # result_ndimg2 = cv2.inRange(i.ndimg, ranges_inner[0], ranges_inner[1])
        # result_ndimg = cv2.bitwise_or(result_ndimg1, result_ndimg2)

    # lower, upper = np.array(lower), np.array(upper)
    # result_ndimg = cv2.inRange(i.ndimg, lower, upper)
    result_ndimg = np.atleast_3d(result_ndimg)
    # cv2.inRange(self.source_img, lower, upper, self.result_img)
    return NdImageData(result_ndimg, "L", i.bool_mask_ndimg)


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
    res = ndimg_to_thresholded_ndimg(thres, ndimg)
    a = np.array((50, 100))
    b = np.array(((10, 20, 30), (40, 50, 10)))
    c = b[0] > b[1]
    bc = np.copy(b)
    bc[0, c] = 0
    bc[1, c] = 255
    print(a, b, c)
