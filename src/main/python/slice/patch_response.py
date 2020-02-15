from typing import NamedTuple, Iterable

from shapely.geometry import Polygon

from img.ndimagedata import NdImageData
from slice.patch_pos import PatchPos
from slice.patch_image_config import PatchImageConfig


class PatchResponse(NamedTuple):
    pos: PatchPos
    polygon: Polygon
    img: NdImageData
    cfg: PatchImageConfig


PatchResponseIterable = Iterable[PatchResponse]