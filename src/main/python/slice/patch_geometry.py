from typing import Tuple, Iterable

from shapely.geometry import Polygon

PatchGeometry = Tuple[Tuple[int, int], Polygon]
PatchGeometryIterable = Iterable[PatchGeometry]