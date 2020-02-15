from typing import Tuple, Iterable

from shapely.geometry import Polygon

from img.ndimagedata import NdImageData

PatchImage = Tuple[Tuple[int, int], Polygon, NdImageData]
PatchImageIterable = Iterable[PatchImage]