from typing import Tuple

import cv2
import numpy as np

from common_image.model.ndimagedata import NdImageData


def resize_ndarray(ndarray: np.ndarray, nrows_ncols: Tuple[int, int], interpolation=None) -> np.ndarray:
    ndarray_ = cv2.resize(ndarray, nrows_ncols[::-1], interpolation=interpolation)
    ndarray_ = np.atleast_3d(ndarray_)
    return ndarray_

def resize_ndimg(ndimg: NdImageData, nrows_ncols: Tuple[int, int]) -> NdImageData:
    ndarray_ = resize_ndarray(ndimg.ndimg, nrows_ncols)
    mask_ = resize_ndarray(ndimg.bool_mask_ndimg, nrows_ncols, interpolation=cv2.INTER_NEAREST) if ndimg.bool_mask_ndimg is not None else None
    return NdImageData(ndarray_, ndimg.color_mode, mask_)