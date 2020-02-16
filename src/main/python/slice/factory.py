from collections import defaultdict
from typing import List, Tuple

import openslide
from shapely.geometry.base import BaseGeometry
from shapely.ops import unary_union
from shapely.prepared import prep
from shapely.strtree import STRtree

from common_shapely.shapely_utils import ProbablyContainsChecker
from slice.generator.geometry.hook.bb_geometry_hook import BBGeometryHook
from slice.generator.geometry.hook.bb_geometry_probably_contains_hook import BBGeometryProbablyContainsHook
from slice.generator.geometry.hook.patch_geometry_hook import PatchGeometryHook
from slice.generator.geometry.hook.patch_geometry_roi_hook import PatchGeometryROIHook
from slice.generator.geometry.patch_geometry_generator_hooks import PatchGeometryGeneratorHooks
from slice.generator.image.annotations_patch_image_generator import AnnotationsPatchImageGenerator
from slice.generator.pos.patch_pos_generator import PatchPosGenerator


def create_annotations_patch_image_generator(annotation_geoms: List[BaseGeometry]) -> AnnotationsPatchImageGenerator:
    z_to_geoms = defaultdict(list)
    for geom in annotation_geoms:
        z = geom.annotation.user_attrs.get('z_index', 0)
        z_to_geoms[z].append(geom)

    z_list = sorted(z_to_geoms.keys())
    zlayers_rtrees = list([STRtree(z_to_geoms[z]) for z in z_list])
    return AnnotationsPatchImageGenerator(zlayers_rtrees)


def create_roi_hooks(roi_geoms: List[BaseGeometry]) -> Tuple[List[BBGeometryHook], List[PatchGeometryHook]]:
    if roi_geoms:
        roi_geoms_union = unary_union(roi_geoms)
        bb_hook = BBGeometryProbablyContainsHook(ProbablyContainsChecker(*roi_geoms_union.bounds))
        roi_geoms_union_prep = prep(roi_geoms_union)
        roi_hook = PatchGeometryROIHook(roi_geoms_union_prep)
        return ([bb_hook], [roi_hook])
    else:
        return ([], [])


def create_annotations_hooks(annotation_geoms: List[BaseGeometry]) -> Tuple[List[BBGeometryHook], List[PatchGeometryHook]]:
    if annotation_geoms:
        # return ([], [PatchGeometryAnnotationsHook(annotation_geoms, STRtree(annotation_geoms))])
        return ([], [])
    else:
        return ([], [])


def create_hooks(annotation_geoms: List[BaseGeometry]) -> Tuple[List[BBGeometryHook], List[PatchGeometryHook]]:
    annotation_hooks = create_annotations_hooks(annotation_geoms)
    roi_geoms = [ag for ag in annotation_geoms if ag.annotation.user_attrs.get('roi')]
    roi_hooks = create_roi_hooks(roi_geoms)
    return ([*annotation_hooks[0], *roi_hooks[0]],
            [*annotation_hooks[1], *roi_hooks[1]])


def create_patch_pos_generator(slide_path: str, stride: int, offset_x: int = 0, offset_y: int = 0) -> PatchPosGenerator:
    with openslide.OpenSlide(slide_path) as slide:
        source_size = slide.level_dimensions[0]
    return PatchPosGenerator(source_size, stride, offset_x, offset_y)


def create_patch_geometry_hooks_generator(grid_length: int, annotation_geoms: List[BaseGeometry]) -> PatchGeometryGeneratorHooks:
    hooks = create_hooks(annotation_geoms)
    return PatchGeometryGeneratorHooks(grid_length, hooks[0], hooks[1])
