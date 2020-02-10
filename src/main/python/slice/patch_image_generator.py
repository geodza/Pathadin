from abc import ABC, abstractmethod
from collections import defaultdict
from typing import Iterable, Tuple, List

import openslide
from dataclasses import field, dataclass
from shapely.geometry import Polygon
from shapely.geometry.base import BaseGeometry
from shapely.strtree import STRtree

from img.ndimagedata import NdImageData
from slice.patch_geometry_generator import PatchGeometryGenerator
from slide_slice_utils import create_layer_polygon_image

PatchImage = Tuple[Tuple[int, int], Polygon, NdImageData]
PatchImageGenerator = Iterable[PatchImage]


class AbstractSlidePatchImageGeneratorFactory(ABC):
    @abstractmethod
    def create(self, slide_path: str, level: int,
               patch_geometry_generator: PatchGeometryGenerator) \
            -> PatchImageGenerator:
        pass


class AbstractSlidePatchImageGeneratorFactoryTemplate(AbstractSlidePatchImageGeneratorFactory):

    def create(self, slide_path: str, level: int,
               patch_geometry_generator: PatchGeometryGenerator) \
            -> PatchImageGenerator:
        with openslide.open_slide(slide_path) as slide:
            # source_size = slide.level_dimensions[0]
            for (x, y), patch in patch_geometry_generator:
                img = self.create_patch_image(slide, patch, level)
                # TODO hook? if we do not like result image (if its fully white or fully black, we may throw it away and continue)
                yield ((x, y), patch, img)

    @abstractmethod
    def create_patch_image(self, slide: openslide.AbstractSlide, patch: Polygon, level: int) -> NdImageData:
        pass


@dataclass
class SlideAnnotationsPatchImageGenerator(AbstractSlidePatchImageGeneratorFactoryTemplate):
    zlayers_rtrees: List[STRtree] = field(default_factory=list)

    def create_patch_image(self, slide: openslide.AbstractSlide, patch: Polygon, level: int) -> NdImageData:
        return create_layer_polygon_image(slide, patch, level, self.zlayers_rtrees)


def create_slide_annotations_patch_image_generator(annotation_geoms: List[BaseGeometry]) -> SlideAnnotationsPatchImageGenerator:
    z_to_geoms = defaultdict(list)
    for geom in annotation_geoms:
        z = geom.annotation.user_attrs.get('z_index', 0)
        z_to_geoms[z].append(geom)

    z_list = sorted(z_to_geoms.keys())
    zlayers_rtrees = list([STRtree(z_to_geoms[z]) for z in z_list])
    return SlideAnnotationsPatchImageGenerator(zlayers_rtrees)