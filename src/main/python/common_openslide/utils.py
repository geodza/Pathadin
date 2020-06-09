from typing import Tuple, Optional

import openslide
from PIL import Image

from common.timeit_utils import timing
from slide_viewer.cache_config import gcached


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


def load_tile(slide_path, level0_pos, level, size):
	with openslide.open_slide(slide_path) as slide:
		tile_pilimage = slide.read_region((int(level0_pos[0]), int(level0_pos[1])), level,
														  (int(size[0]), int(size[1])))
		return tile_pilimage