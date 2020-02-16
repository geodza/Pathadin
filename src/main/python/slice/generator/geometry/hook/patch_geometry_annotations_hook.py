from abc import abstractmethod
from typing import List, Tuple

from dataclasses import dataclass, field
from shapely.geometry import Polygon
from shapely.geometry.base import BaseGeometry
from shapely.strtree import STRtree

from slice.model.patch_geometry import PatchGeometry
from slice.generator.geometry.hook.patch_geometry_hook import PatchGeometryHook


@dataclass()
class PatchGeometryAnnotationsHook(PatchGeometryHook):
    annotation_geoms: List[BaseGeometry] = field(default_factory=list)
    rtree: STRtree = field(default_factory=Polygon)

    def filter(self, patch_geometry: PatchGeometry) -> bool:
        pos, polygon = patch_geometry
        annotation_geoms, rtree = self.annotation_geoms, self.rtree
        probable_intersecting_geoms = rtree.query(polygon)
        intersecting_geoms = [g for g in probable_intersecting_geoms if g.intersects(polygon)]
        intersecting_geoms_intersections = [g.intersection(polygon) for g in intersecting_geoms]
        return self.patch_intersections_filter_hook(polygon, annotation_geoms, list(zip(intersecting_geoms, intersecting_geoms_intersections)))

    @abstractmethod
    def patch_intersections_filter_hook(self, patch: Polygon, annotation_geoms: List[BaseGeometry],
                                        intersecting_geoms_intersections: List[Tuple[BaseGeometry, BaseGeometry]]) -> bool:
        pass