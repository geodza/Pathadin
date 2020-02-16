from abc import ABC, abstractmethod
from typing import Tuple, List

from dataclasses import dataclass, field
from shapely.geometry import box
from shapely.geometry.base import BaseGeometry
from shapely.ops import unary_union
from shapely.prepared import prep

from common_shapely.shapely_utils import ProbablyContainsChecker
from slice.generator.geometry.hook.bb_hook import BBGeometryHook, BBGeometryProbablyContainsHook
from slice.model.patch_geometry import PatchGeometryIterable, PatchGeometry
from slice.generator.geometry.hook.patch_geometry_hook import PatchGeometryHook
from slice.generator.geometry.hook.patch_geometry_roi_hook import PatchGeometryROIHook


# @dataclass()
# class PatchPos():
#     x: int
#     y: int


# @dataclass()
# class PatchGeometry():
#     pos: PatchPos
#     polygon: Polygon
from slice.model.patch_pos import PatchPosIterable
from slice.generator.patch_pos_generator import PatchPosGenerator


class PatchGeometryGenerator(ABC):
    @abstractmethod
    def create(self, patch_positions: PatchPosIterable, grid_length: int) -> PatchGeometryIterable:
        pass


class PatchGeometryGeneratorHooksTemplate(PatchGeometryGenerator):

    def create(self, patch_positions: PatchPosIterable, grid_length: int) -> PatchGeometryIterable:
        for x, y in patch_positions:
            if not self.patch_bb_filter_hook((x, y), (x + grid_length, y + grid_length)):
                continue
            patch = box(x, y, x + grid_length, y + grid_length)
            if not self.patch_filter_hook(((x, y), patch)):
                continue
            yield ((x, y), patch)
            # yield PatchGeometry((x, y), patch)

    def patch_bb_filter_hook(self, p1: Tuple[int, int], p2: Tuple[int, int]) -> bool:
        return True

    def patch_filter_hook(self, patch_geometry: PatchGeometry) -> bool:
        return True


@dataclass()
class PatchGeometryGeneratorHooks(PatchGeometryGeneratorHooksTemplate):
    bb_hooks: List[BBGeometryHook] = field(default_factory=list)
    patch_hooks: List[PatchGeometryHook] = field(default_factory=list)

    def patch_bb_filter_hook(self, p1: Tuple[int, int], p2: Tuple[int, int]) -> bool:
        for h in self.bb_hooks:
            if not h.filter(p1, p2):
                return False
        return True

    def patch_filter_hook(self, patch_geometry: PatchGeometry) -> bool:
        for h in self.patch_hooks:
            if not h.filter(patch_geometry):
                return False
        return True


def create_roi_hooks(roi_geoms: List[BaseGeometry]) -> Tuple[List[BBGeometryHook], List[PatchGeometryHook]]:
    if roi_geoms:
        roi_geoms_union = unary_union(roi_geoms)
        bb_hook = BBGeometryProbablyContainsHook(ProbablyContainsChecker(*roi_geoms_union.bounds))
        roi_geoms_union_prep = prep(roi_geoms_union)
        roi_hook = PatchGeometryROIHook(roi_geoms_union_prep)
        return ([bb_hook], [roi_hook])
    else:
        return ([], [])


def create_annotation_hooks(annotation_geoms: List[BaseGeometry]) -> Tuple[List[BBGeometryHook], List[PatchGeometryHook]]:
    if annotation_geoms:
        # return ([], [PatchGeometryAnnotationsHook(annotation_geoms, STRtree(annotation_geoms))])
        return ([], [])
    else:
        return ([], [])


def create_hooks(annotation_geoms: List[BaseGeometry]) -> Tuple[List[BBGeometryHook], List[PatchGeometryHook]]:
    annotation_hooks = create_annotation_hooks(annotation_geoms)
    roi_geoms = [ag for ag in annotation_geoms if ag.annotation.user_attrs.get('roi')]
    roi_hooks = create_roi_hooks(roi_geoms)
    return ([*annotation_hooks[0], *roi_hooks[0]],
            [*annotation_hooks[1], *roi_hooks[1]])


def create_patch_geometry_hooks_generator_factory(annotation_geoms: List[BaseGeometry]) -> PatchGeometryGeneratorHooks:
    hooks = create_hooks(annotation_geoms)
    pggf = PatchGeometryGeneratorHooks(hooks[0], hooks[1])
    return pggf


if __name__ == '__main__':
    roipg = PatchGeometryGeneratorHooks(
        [BBGeometryProbablyContainsHook(ProbablyContainsChecker(512, 512, 1024, 1024))],
        []
    )
    poss=PatchPosGenerator().create((1000,1000),256)
    gen = roipg.create(poss, 256)
    print(gen)
    for i in gen:
        print(i)

