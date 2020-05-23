from typing import Tuple, Iterable

import numpy as np

from common.timeit_utils import timing
from common_image.core.draw import draw_ellipse, draw_rect, draw_polygon, draw_line
from slide_viewer.cache_config import gcached
from slide_viewer.ui.common.annotation_type import AnnotationType

ituple = Tuple[int, int]


def draw_annotation(ndarray: np.ndarray, points: Iterable[ituple], annotationType: AnnotationType = AnnotationType.RECT,
                    color: int = 255) -> None:
    if annotationType is AnnotationType.RECT:
        p1, p2 = points
        draw_rect(ndarray, p1, p2, color)
    elif annotationType is AnnotationType.ELLIPSE:
        p1, p2 = points
        draw_ellipse(ndarray, p1, p2, color)
    elif annotationType is AnnotationType.POLYGON:
        draw_polygon(ndarray, points, color)
    elif annotationType is AnnotationType.LINE:
        p1, p2 = points
        draw_line(ndarray, p1, p2)
    else:
        raise ValueError()


@timing
@gcached
def build_mask(img_shape: Tuple[int, ...], points: Iterable[ituple],
               annotationType: AnnotationType = AnnotationType.RECT, background_color: int = 0, color: int = 255) -> np.ndarray:
    r, c, *a = img_shape
    mask_img = np.full((r, c), background_color, dtype=np.uint8, order='C')
    # points_ = np.array([point_to_tuple(p) for p in points])
    draw_annotation(mask_img, points, annotationType, color)

    return mask_img