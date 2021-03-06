from typing import List

import openslide
from dataclasses import dataclass, field
from shapely.geometry import Polygon
from shapely.strtree import STRtree

from common_image.model.ndimg import Ndimg
from slice.generator.image.patch_image_generator_template import PatchImageGeneratorTemplate
from slice.image_shapely_utils import create_layer_polygon_image


@dataclass
class AnnotationsPatchImageGenerator(PatchImageGeneratorTemplate):
    zlayers_rtrees: List[STRtree] = field(default_factory=list)

    def create_patch_image(self, slide: openslide.AbstractSlide, patch: Polygon, level: int, target_color_mode='RGB',
                           rescale_result_image=True) -> Ndimg:
        return create_layer_polygon_image(slide, patch, level, self.zlayers_rtrees, target_color_mode, rescale_result_image)
