from typing import List, Tuple

from dataclasses import dataclass, field

from slice.generator.geometry.hook.bb_geometry_hook import BBGeometryHook
from slice.generator.geometry.hook.patch_geometry_hook import PatchGeometryHook
from slice.generator.geometry.patch_geometry_generator_hooks_template import PatchGeometryGeneratorHooksTemplate
from slice.model.patch_geometry import PatchGeometry


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