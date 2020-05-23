import cv2
from PyQt5.QtGui import QPolygon

from common.points_utils import deshift_points, rescale_points
from common.timeit_utils import timing
from common_image.core.object_convert import pilimg_to_ndimg
from common_image.model.ndimg import Ndimg
from common_qt.util.qobjects_convert_util import ituple_to_qpoint
from img.proc.mask import build_mask
from img.proc.region import RegionData, read_region
from slide_viewer.ui.common.model import AnnotationModel


def build_region_data(img_path: str, model: AnnotationModel, filter_level: int) -> RegionData:
	origin_point = model.geometry.origin_point
	points = tuple(model.geometry.points)
	return RegionData(img_path, filter_level, origin_point, points, model.geometry.annotation_type)


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
