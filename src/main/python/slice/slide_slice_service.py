from typing import Iterable, Tuple, Optional, List

from dataclasses import dataclass, field
from openslide import OpenSlide
from shapely.geometry.base import BaseGeometry

from img.ndimagedata import NdImageData
from shapely_utils import annotation_to_geom
from slide_viewer.ui.odict.deep.model import AnnotationTreeItems


def load_annotation_geoms(annotations_path: str) -> List[BaseGeometry]:
    annotations_container = AnnotationTreeItems.parse_file(annotations_path)
    annotations = annotations_container.annotations

    train_annotations = [a for a in annotations.values() if a.label != 'test']

    annotation_geoms = [annotation_to_geom(a, True) for a in train_annotations]
    return annotation_geoms

#
# @dataclass
# class SlideSliceService:
#     annotations_path: Optional[str] = None
#
#     # annotation_geoms: List[BaseGeometry] = field(init=False)
#     patch_geometry_generator: AbstractPatchGeometryGeneratorFactory = field(init=False)
#     patch_image_generator: PatchImageGeneratorFactory = field(init=False)
#
#     def __post_init__(self):
#         annotations_path = self.annotations_path
#         annotation_geoms = load_annotation_geoms(annotations_path) if annotations_path else []
#         self.patch_geometry_generator = ROIPatchGeometryGeneratorFactory(annotation_geoms)
#         self.patch_image_generator = SlideAnnotationsPatchImageGenerator(annotation_geoms)
#
#     def create(self, slide_path: str, level: int, source_size: Tuple[int, int], grid_length: int,
#                stride: int = None, x_offset: int = 0, y_offset: int = 0) \
#             -> Iterable[Tuple[Tuple[int, int], NdImageData]]:
#         patches = self.patch_geometry_generator.create(source_size, grid_length, stride, x_offset, y_offset)
#         images = self.patch_image_generator.create(slide_path, level, patches)
#         return images
#
#
# def process_ssc(ssc: SlideSliceConfig) -> Iterable[Tuple[Tuple[int, int], NdImageData]]:
#     # patch_generator = PatchGeometryHooksGeneratorFactory().create()
#     # patch_image_generator_factory = SlideAnnotationsPatchImageGenerator([])
#     # patch_image_generator = patch_image_generator_factory.create(1, 2, patch_generator)
#     sss = SlideSliceService(ssc.annotations_path)
#     with OpenSlide(ssc.slide_path) as slide:
#         source_size = slide.level_dimensions[0]
#     gen = sss.create(ssc.slide_path, ssc.level, source_size, ssc.grid_length, ssc.stride, ssc.offset_x, ssc.offset_y)
#     return gen
#
#
# def process_sscs(sscs: List[SlideSliceConfig]) -> Iterable[Tuple[Tuple[int, int], NdImageData, SlideSliceConfig]]:
#     for ssc in sscs:
#         pos_list = []
#         for ((x, y), img) in process_ssc(ssc):
#             pos_list.append((x, y))
#             yield ((x,y),img,ssc)
#
#
#     sss = SlideSliceService(ssc.annotations_path)
#     with OpenSlide(ssc.slide_path) as slide:
#         source_size = slide.level_dimensions[0]
#     gen = sss.create(ssc.slide_path, ssc.level, source_size, ssc.grid_length, ssc.stride, ssc.offset_x, ssc.offset_y)
#     return gen
