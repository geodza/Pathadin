from typing import Tuple, Optional, NamedTuple

import openslide
from PIL import Image
from PyQt5.QtGui import QPolygon

from common.timeit_utils import timing
from common_qt.util.qobjects_convert_util import ituple_to_qpoint, qpoint_to_ituple
from slide_viewer.cache_config import gcached
from slide_viewer.ui.common.annotation_type import AnnotationType

ituple = Tuple[int, int]
ituples = Tuple[ituple, ...]


class RegionData(NamedTuple):
	img_path: str
	level: Optional[int] = None
	origin_point: Optional[Tuple[int, int]] = None
	points: Optional[Tuple[Tuple[int, int], ...]] = None
	annotation_type: AnnotationType = AnnotationType.RECT


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


@timing
@gcached
def load_region(img_path: str, pos: Tuple[int, int] = (0, 0), level: Optional[int] = None,
				size: Tuple[int, int] = None) -> Image.Image:
	with openslide.open_slide(img_path) as slide:
		if level is None or level == "":
			level = min(2, slide.level_count - 1)
		level = int(level)
		if level < 0:
			level = list(range(slide.level_count))[-level]
		# TODO add literals for level like MAX_LEVEL, AUTO_LEVEL(about memory considerations)
		# print(f"load_region on level: {level}")
		level_downsample = slide.level_downsamples[level]
		if size is not None:
			size = (int(size[0] / level_downsample), int(size[1] / level_downsample))
		region = slide.read_region(pos, level, size)
		return region
