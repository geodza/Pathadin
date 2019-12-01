from typing import Tuple

import cv2
import numpy as np
from PIL import Image

from slide_viewer.cache_config import gcached
from slide_viewer.filter.image_processing import ituples
from slide_viewer.ui.common.img.img_object_convert import expose_pilimage_buffer_to_ndarray, \
    expose_ndarray_buffer_to_pillowimage


@gcached("build_mask")
def build_mask(img_shape: Tuple[int, ...], points: ituples) -> np.ndarray:
    r, c, *a = img_shape
    mask_img = np.zeros((r, c), dtype=np.uint8, order='C')
    # points_ = np.array([point_to_tuple(p) for p in points])
    points_ = np.array(points).reshape((1, -1, 2), order='C')
    cv2.fillPoly(mask_img, points_, 255)
    return mask_img


def mask_img(img: Image.Image, points: ituples) -> Image.Image:
    img_arr = getattr(img, 'arr') if hasattr(img, 'arr') else expose_pilimage_buffer_to_ndarray(img)
    mask = build_mask(img_arr.shape, points)
    # (0,0,0,0) for rgba means transparent
    masked_img_arr = cv2.bitwise_and(img_arr, img_arr, mask=mask)
    masked_img = expose_ndarray_buffer_to_pillowimage(masked_img_arr, img.mode)
    return masked_img

def mask_ndimg(img_arr: np.ndarray, points: ituples) -> np.ndarray:
    mask = build_mask(img_arr.shape, points)
    # (0,0,0,0) for rgba means transparent
    masked_img_arr = cv2.bitwise_and(img_arr, img_arr, mask=mask)
    return masked_img_arr