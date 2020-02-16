from typing import Tuple

import cv2
import numpy as np

from img.ndimagedata import NdImageData


def imgresize(ndimg: NdImageData, nrows_ncols: Tuple[int, int]) -> NdImageData:
    print(f"resize: {ndimg.ndimg.shape}->{nrows_ncols}")
    ndimg_ = cv2.resize(ndimg.ndimg, nrows_ncols[::-1])
    ndimg_ = np.atleast_3d(ndimg_)
    mask_ = cv2.resize(ndimg.bool_mask_ndimg, nrows_ncols[::-1], interpolation=cv2.INTER_NEAREST) if ndimg.bool_mask_ndimg is not None else None
    mask_ = np.atleast_3d(mask_) if mask_ is not None else None
    return NdImageData(ndimg_, ndimg.color_mode, mask_)


nchannels_to_empty_color = {1: (0,), 3: (0, 255, 0), 4: (0, 0, 0, 255)}
color_mode_to_empty_color = {'L': (0,), 'RGB': (0, 255, 0), 'RGBA': (0, 0, 0, 255)}


def create_empty_image(nrows: int, ncols: int, color_mode: str) -> NdImageData:
    # return np.empty((nrows, ncols, nchannels), dtype=np.uint8)
    nchannels = len(color_mode)
    ndimg_ = np.zeros((nrows, ncols, nchannels), dtype=np.uint8)
    # ndimg_ = np.tile(np.array(color_mode_to_empty_color[color_mode], dtype=np.uint8), (nrows, ncols, 1))
    return NdImageData(ndimg_, color_mode, None)