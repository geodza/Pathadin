from typing import Iterable, Tuple

import cv2
import numpy as np
from PIL import Image
from PyQt5.QtGui import QPolygon

from annotation.annotation_type import AnnotationType
from annotation.model import AnnotationModel
from annotation_image.reagion_data import RegionData
from common.points_utils import deshift_points, rescale_points
from common.timeit_utils import timing
from common_image.core.draw import draw_rect, draw_ellipse, draw_polygon, draw_line
from common_image.core.object_convert import pilimg_to_ndimg
from common_image.model.ndimg import Ndimg
from common_openslide.utils import load_region
from common_qt.util.qobjects_convert_util import ituple_to_qpoint, qpoint_to_ituple
from slide_viewer.cache_config import gcached

ituple = Tuple[int, int]


def build_region_data(img_path: str, model: AnnotationModel, filter_level: int) -> RegionData:
	origin_point = model.geometry.origin_point
	points = tuple(model.geometry.points)
	return RegionData(img_path, filter_level, origin_point, points, model.geometry.annotation_type)


@timing
def read_region(data: RegionData) -> Image.Image:
	if data.points is not None and data.origin_point is not None:
		polygon = QPolygon([ituple_to_qpoint(p) for p in data.points])
		top_left = ituple_to_qpoint(data.origin_point) + polygon.boundingRect().topLeft()
		pos = qpoint_to_ituple(top_left)
		size = polygon.boundingRect().size()
		size = (size.width(), size.height())
		return load_region(data.img_path, pos, data.level, size)
	else:
		return load_region(data.img_path)


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
			   annotationType: AnnotationType = AnnotationType.RECT, background_color: int = 0,
			   color: int = 255) -> np.ndarray:
	r, c, *a = img_shape
	mask_img = np.full((r, c), background_color, dtype=np.uint8, order='C')
	# points_ = np.array([point_to_tuple(p) for p in points])
	draw_annotation(mask_img, points, annotationType, color)

	return mask_img


@timing
def read_masked_region(rd: RegionData) -> Ndimg:
	pilimg = read_region(rd)
	level0_qsize = QPolygon([ituple_to_qpoint(p) for p in rd.points]).boundingRect().size()
	sx, sy = pilimg.width / level0_qsize.width(), pilimg.height / level0_qsize.height()
	ndimg = pilimg_to_ndimg(pilimg)
	points = deshift_points(rd.points, rd.origin_point)
	points = rescale_points(points, sx, sy)
	# ituples = ituples_to_polygon_ituples(rd.points)
	mask = build_mask(ndimg.ndarray.shape, points, rd.annotation_type, background_color=0, color=255)
	# (0,0,0,0) for rgba means transparent
	masked_ndimg = cv2.bitwise_and(ndimg.ndarray, ndimg.ndarray, mask=mask)
	# ndimg.ndimg = mask_ndimg(ndimg.ndimg, points, rd.annotation_type)
	ndimg.ndarray = masked_ndimg
	# mask = cv2.bitwise_not(mask)
	ndimg.bool_mask_ndarray = mask != 0
	return ndimg
