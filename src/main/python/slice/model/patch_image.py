from typing import Tuple, Iterable

from shapely.geometry import Polygon

from img.ndimagedata import NdImageData
from slice.model.patch_pos import PatchPos

PatchImage = Tuple[PatchPos, Polygon, NdImageData]
PatchImageIterable = Iterable[PatchImage]
