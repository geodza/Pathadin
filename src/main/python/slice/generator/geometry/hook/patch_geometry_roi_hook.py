from dataclasses import dataclass
from shapely.geometry.base import BaseGeometry

from slice.model.patch_geometry import PatchGeometry
from slice.generator.geometry.hook.patch_geometry_hook import PatchGeometryHook


@dataclass()
class PatchGeometryROIHook(PatchGeometryHook):
    roi_annotations_geoms_union: BaseGeometry

    def filter(self, patch_geometry: PatchGeometry) -> bool:
        pos, polygon = patch_geometry
        return self.roi_annotations_geoms_union.contains(polygon)