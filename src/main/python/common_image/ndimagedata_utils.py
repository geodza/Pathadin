from typing import Tuple

import cv2
import numpy as np

from common_image.ndimagedata import NdImageData


def resize_ndarray(ndarray: np.ndarray, nrows_ncols: Tuple[int, int], interpolation=None) -> np.ndarray:
    ndarray_ = cv2.resize(ndarray, nrows_ncols[::-1], interpolation=interpolation)
    ndarray_ = np.atleast_3d(ndarray_)
    return ndarray_


def resize_ndimg(ndimg: NdImageData, nrows_ncols: Tuple[int, int]) -> NdImageData:
    ndarray_ = resize_ndarray(ndimg.ndimg, nrows_ncols)
    mask_ = resize_ndarray(ndimg.bool_mask_ndimg, nrows_ncols, interpolation=cv2.INTER_NEAREST) if ndimg.bool_mask_ndimg is not None else None
    return NdImageData(ndarray_, ndimg.color_mode, mask_)


nchannels_to_empty_color = {1: (0,), 3: (0, 255, 0), 4: (0, 0, 0, 255)}
color_mode_to_empty_color = {'L': (0,), 'RGB': (0, 255, 0), 'RGBA': (0, 0, 0, 255)}


def create_empty_ndarray(nrows: int, ncols: int, color_mode: str) -> np.ndarray:
    # return np.empty((nrows, ncols, nchannels), dtype=np.uint8)
    nchannels = len(color_mode)
    # ndimg_ = np.tile(np.array(color_mode_to_empty_color[color_mode], dtype=np.uint8), (nrows, ncols, 1))
    ndimg_ = np.zeros((nrows, ncols, nchannels), dtype=np.uint8)
    return ndimg_


def create_empty_ndimg(nrows: int, ncols: int, color_mode: str) -> NdImageData:
    # return np.empty((nrows, ncols, nchannels), dtype=np.uint8)
    ndimg_ = create_empty_ndarray(nrows, ncols, color_mode)
    return NdImageData(ndimg_, color_mode, None)
