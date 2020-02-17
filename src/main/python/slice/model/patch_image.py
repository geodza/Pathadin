from typing import Tuple, Iterable

from shapely.geometry import Polygon

from common_image.model.ndimg import Ndimg
from slice.model.patch_pos import PatchPos

PatchImage = Tuple[PatchPos, Polygon, Ndimg]
PatchImageIterable = Iterable[PatchImage]
