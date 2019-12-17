from typing import Tuple

import cv2
import numpy as np

from img.model import ituples
from slide_viewer.cache_config import gcached
from slide_viewer.ui.model.annotation_type import AnnotationType


@gcached
def build_mask(img_shape: Tuple[int, ...], points: ituples,
               annotationType: AnnotationType = AnnotationType.RECT) -> np.ndarray:
    r, c, *a = img_shape
    mask_img = np.zeros((r, c), dtype=np.uint8, order='C')
    # points_ = np.array([point_to_tuple(p) for p in points])
    if annotationType is AnnotationType.RECT:
        p1, p2 = points
        cv2.rectangle(mask_img, p1, p2, 255, cv2.FILLED)
    elif annotationType is AnnotationType.ELLIPSE:
        p1, p2 = points
        ax = int(abs(p2[0] - p1[0]) / 2)
        ay = int(abs(p2[1] - p1[1]) / 2)
        cx = int(abs(p2[0] + p1[0]) / 2)
        cy = int(abs(p2[1] + p1[1]) / 2)
        cv2.ellipse(mask_img, (cx, cy), (ax, ay), 0, 0, 360, 255, cv2.FILLED)
        # cv2.ellipse(mask_img, points, 255, cv2.FILLED)
    elif annotationType is AnnotationType.POLYGON:
        points_ = np.array(points).reshape((1, -1, 2), order='C')
        cv2.fillPoly(mask_img, points_, 255)
    elif annotationType is AnnotationType.LINE:
        p1, p2 = points
        cv2.line(mask_img, p1, p2, 50)
    else:
        raise ValueError()

    return mask_img


def mask_ndimg(ndimg: np.ndarray, points: ituples, annotationType: AnnotationType = AnnotationType.RECT) -> np.ndarray:
    mask = build_mask(ndimg.shape, points, annotationType)
    # (0,0,0,0) for rgba means transparent
    masked_img_arr = cv2.bitwise_and(ndimg, ndimg, mask=mask)
    return masked_img_arr

# def mask_ndimg2(img: NdImageData, points: ituples) -> NdImageData:
#     masked_ndimg = mask_ndimg(img.ndimg, points)
#     masked_img = NdImageData(masked_ndimg, img.color_mode)
#     return masked_img
