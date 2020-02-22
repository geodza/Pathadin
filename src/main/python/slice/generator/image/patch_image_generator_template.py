from abc import abstractmethod

import openslide
from dataclasses import dataclass
from shapely.geometry import Polygon

from common_image.model.ndimg import Ndimg
from slice.generator.image.patch_image_generator import PatchImageGenerator
from slice.model.patch_geometry import PatchGeometryIterable
from slice.model.patch_image import PatchImageIterable


@dataclass
class PatchImageGeneratorTemplate(PatchImageGenerator):
    slide_path: str
    level: int
    rescale_result_image: bool

    def create(self, patch_geometries: PatchGeometryIterable) -> PatchImageIterable:
        slide_path, level, rescale_result_image = self.slide_path, self.level, self.rescale_result_image
        with openslide.open_slide(slide_path) as slide:
            for (x, y), patch in patch_geometries:
                img = self.create_patch_image(slide, patch, level, rescale_result_image)
                # TODO hook? if we do not like result image (if its fully white or fully black, we may throw it away and continue)
                yield ((x, y), patch, img)

    @abstractmethod
    def create_patch_image(self, slide: openslide.AbstractSlide, patch: Polygon, level: int, rescale_result_image=True) -> Ndimg:
        pass
