import cv2
import numpy as np

from img.ndimagedata import NdImageData


def ndimg_to_thresholded_ndimg(threshold_range, i: NdImageData) -> NdImageData:
    lower, upper = threshold_range
    lower, upper = np.array(lower), np.array(upper)
    result_ndimg = cv2.inRange(i.ndimg, lower, upper)
    result_ndimg = np.atleast_3d(result_ndimg)
    # cv2.inRange(self.source_img, lower, upper, self.result_img)
    return NdImageData(result_ndimg, "L", i.bool_mask_ndimg)
