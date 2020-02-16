from typing import Tuple

from dataclasses import dataclass
from shapely.geometry import box

from slice.generator.geometry.patch_geometry_generator import PatchGeometryGenerator
from slice.model.patch_geometry import PatchGeometryIterable, PatchGeometry
from slice.model.patch_pos import PatchPosIterable


@dataclass
class PatchGeometryGeneratorHooksTemplate(PatchGeometryGenerator):
    grid_length: int

    def create(self, patch_positions: PatchPosIterable) -> PatchGeometryIterable:
        grid_length = self.grid_length
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
