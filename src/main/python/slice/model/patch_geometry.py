from typing import Tuple, Iterable

from shapely.geometry import Polygon

from slice.model.patch_pos import PatchPos

PatchGeometry = Tuple[PatchPos, Polygon]
PatchGeometryIterable = Iterable[PatchGeometry]
