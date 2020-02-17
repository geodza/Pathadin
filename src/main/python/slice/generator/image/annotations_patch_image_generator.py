from typing import List

import openslide
from dataclasses import dataclass, field
from shapely.geometry import Polygon
from shapely.strtree import STRtree

from common_image.ndimagedata import NdImageData
from slice.generator.image.patch_image_generator_template import PatchImageGeneratorTemplate
from slice.image_shapely_utils import create_layer_polygon_image


@dataclass
class AnnotationsPatchImageGenerator(PatchImageGeneratorTemplate):
    zlayers_rtrees: List[STRtree] = field(default_factory=list)

    def create_patch_image(self, slide: openslide.AbstractSlide, patch: Polygon, level: int) -> NdImageData:
        return create_layer_polygon_image(slide, patch, level, self.zlayers_rtrees)
