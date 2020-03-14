from typing import Tuple, Dict, List

import openslide
from PIL.Image import Image
from PyQt5.QtCore import QRectF

from common_image_qt.core import pilimage_to_pixmap


class SlideHelper:

    def __init__(self, slide_path: str):
        self.slide_path = slide_path
        with openslide.open_slide(slide_path) as slide:
            self.level_downsamples = slide.level_downsamples
            self.level_dimensions = slide.level_dimensions
            self.level_count = slide.level_count
            self.properties = dict(slide.properties) if slide.properties else {}
            self.microns_per_pixel = float(self.properties.get(openslide.PROPERTY_NAME_MPP_X, 1))
            self.objective_power = float(self.properties.get(openslide.PROPERTY_NAME_OBJECTIVE_POWER, 1))

    def get_slide_path(self) -> str:
        return self.slide_path

    def get_downsample_for_level(self, level: int) -> int:
        return self.level_downsamples[level]

    def get_level_size(self, level: int) -> Tuple[int, int]:
        return self.level_dimensions[level]

    def get_rect_for_level(self, level: int) -> QRectF:
        size_ = self.get_level_size(level)
        rect = QRectF(0, 0, size_[0], size_[1])
        return rect

    def get_max_level(self) -> int:
        return len(self.level_downsamples) - 1

    def get_levels(self) -> List[int]:
        return list(range(self.level_count))

    def get_best_level_for_downsample(self, downsample: int) -> int:
        with openslide.open_slide(self.slide_path) as slide:
            return slide.get_best_level_for_downsample(downsample)

    def get_properties(self) -> Dict:
        return self.properties

    def scale_to_zoom(self, scale: float) -> float:
        return self.objective_power * scale

    def zoom_to_scale(self, zoom: float) -> float:
        return zoom / self.objective_power

    def pixels_to_microns(self, pixels: float) -> float:
        return pixels * self.microns_per_pixel

    def microns_to_pixels(self, microns: float) -> float:
        return microns / self.microns_per_pixel

    def downsample_to_zoom(self, downsample: int) -> float:
        return self.objective_power / downsample

    def read_region_pilimage(self, level0_pos: Tuple[int, int] = (0, 0), level: int = 0,
                             size: Tuple[int, int] = None) -> Image:
        level0_pos = level0_pos or (0, 0)
        level = level or 0
        with openslide.open_slide(self.slide_path) as slide:
            size = size or slide.level_dimensions[level]
            tile_pilimage = slide.read_region((int(level0_pos[0]), int(level0_pos[1])), level,
                                              (int(size[0]), int(size[1])))
            return tile_pilimage

    def read_region_pixmap(self, level0_pos: Tuple[int, int] = (0, 0), level: int = 0,
                           size: Tuple[int, int] = None):
        tile_pilimage = self.read_region_pilimage(level0_pos, level, size)
        pixmap = pilimage_to_pixmap(tile_pilimage)
        return pixmap
