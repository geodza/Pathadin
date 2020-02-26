from typing import List, Tuple

import openslide
from shapely.geometry.base import BaseGeometry
from shapely.ops import unary_union
from shapely.prepared import prep

from common_shapely.shapely_utils import ProbablyContainsChecker
from slice.generator.geometry.hook.bb_geometry_hook import BBGeometryHook
from slice.generator.geometry.hook.bb_geometry_probably_contains_hook import BBGeometryProbablyContainsHook
from slice.generator.geometry.hook.patch_geometry_hook import PatchGeometryHook
from slice.generator.geometry.hook.patch_geometry_roi_hook import PatchGeometryROIHook
from slice.generator.geometry.patch_geometry_generator_hooks import PatchGeometryGeneratorHooks
from slice.generator.pos.patch_pos_generator import PatchPosGenerator


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


def create_patch_pos_generator(slide_path: str, x_stride: int, y_stride: int, offset_x: int = 0, offset_y: int = 0) -> PatchPosGenerator:
    with openslide.open_slide(slide_path) as slide:
        source_size = slide.level_dimensions[0]
    return PatchPosGenerator(source_size, x_stride, y_stride, offset_x, offset_y)


def create_patch_geometry_hooks_generator(slide_path: str, patch_size: Tuple[int, int],
                                          annotation_geoms: List[BaseGeometry]) -> PatchGeometryGeneratorHooks:
    hooks = create_hooks(annotation_geoms)
    if patch_size[0] <= 0 or patch_size[1] <= 0:
        with openslide.open_slide(slide_path) as slide:
            w = slide.level_dimensions[0][0] if patch_size[0] <= 0 else patch_size[0]
            h = slide.level_dimensions[0][1] if patch_size[1] <= 0 else patch_size[1]
            patch_size = w, h
    return PatchGeometryGeneratorHooks(patch_size, hooks[0], hooks[1])
    # return PatchGeometryGeneratorHooks(patch_size, [], [])
