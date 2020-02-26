from typing import Iterable, NamedTuple

from shapely.geometry import Polygon

from common_image.model.ndimg import Ndimg
from slice.model.patch_pos import PatchPos


class PatchImage(NamedTuple):
    pos: PatchPos
    polygon: Polygon
    img: Ndimg


PatchImageIterable = Iterable[PatchImage]
