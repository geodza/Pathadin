from typing import Tuple, Iterable

from shapely.geometry import Polygon

from common_image.model.ndimagedata import NdImageData
from slice.model.patch_pos import PatchPos

PatchImage = Tuple[PatchPos, Polygon, NdImageData]
PatchImageIterable = Iterable[PatchImage]
