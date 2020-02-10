from abc import ABC, abstractmethod
from typing import List, Tuple

from dataclasses import dataclass, field
from shapely.geometry import Polygon
from shapely.geometry.base import BaseGeometry
from shapely.strtree import STRtree


class PatchGeometryHook(ABC):
    @abstractmethod
    def filter(self, patch: Polygon) -> bool:
        pass


@dataclass()
class PatchGeometryROIHook(PatchGeometryHook):
    roi_annotations_geoms_union: BaseGeometry

    def filter(self, patch: Polygon) -> bool:
        return self.roi_annotations_geoms_union.contains(patch)


@dataclass()
class PatchGeometryAnnotationsHook(PatchGeometryHook):
    annotation_geoms: List[BaseGeometry] = field(default_factory=list)
    rtree: STRtree = field(default_factory=Polygon)

    def patch_filter_hook(self, patch: Polygon) -> bool:
        annotation_geoms, rtree = self.annotation_geoms, self.rtree
        probable_intersecting_geoms = rtree.query(patch)
        intersecting_geoms = [g for g in probable_intersecting_geoms if g.intersects(patch)]
        intersecting_geoms_intersections = [g.intersection(patch) for g in intersecting_geoms]
        return self.patch_intersections_filter_hook(patch, annotation_geoms, list(zip(intersecting_geoms, intersecting_geoms_intersections)))

    @abstractmethod
    def patch_intersections_filter_hook(self, patch: Polygon, annotation_geoms: List[BaseGeometry],
                                        intersecting_geoms_intersections: List[Tuple[BaseGeometry, BaseGeometry]]) -> bool:
        pass
