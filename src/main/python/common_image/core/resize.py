from typing import Tuple

import cv2
import numpy as np

from common_image.model.ndimg import Ndimg


def resize_ndarray(ndarray: np.ndarray, nrows_ncols: Tuple[int, int], interpolation=None) -> np.ndarray:
    ndarray_ = cv2.resize(ndarray, nrows_ncols[::-1], interpolation=interpolation)
    ndarray_ = np.atleast_3d(ndarray_)
    return ndarray_

def resize_ndimg(ndimg: Ndimg, nrows_ncols: Tuple[int, int]) -> Ndimg:
    ndarray_ = resize_ndarray(ndimg.ndarray, nrows_ncols)
    mask_ = resize_ndarray(ndimg.bool_mask_ndarray, nrows_ncols, interpolation=cv2.INTER_NEAREST) if ndimg.bool_mask_ndarray is not None else None
    return Ndimg(ndarray_, ndimg.color_mode, mask_)