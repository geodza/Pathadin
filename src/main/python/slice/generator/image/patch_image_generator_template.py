from abc import abstractmethod

import openslide
from shapely.geometry import Polygon

from img.ndimagedata import NdImageData
from slice.generator.image.patch_image_generator import PatchImageGenerator
from slice.model.patch_geometry import PatchGeometryIterable
from slice.model.patch_image import PatchImageIterable


class PatchImageGeneratorTemplate(PatchImageGenerator):

    def create(self, slide_path: str, level: int,
               patch_geometries: PatchGeometryIterable) -> PatchImageIterable:
        with openslide.open_slide(slide_path) as slide:
            # source_size = slide.level_dimensions[0]
            for (x, y), patch in patch_geometries:
                img = self.create_patch_image(slide, patch, level)
                # TODO hook? if we do not like result image (if its fully white or fully black, we may throw it away and continue)
                yield ((x, y), patch, img)

    @abstractmethod
    def create_patch_image(self, slide: openslide.AbstractSlide, patch: Polygon, level: int) -> NdImageData:
        pass
