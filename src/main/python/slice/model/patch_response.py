from typing import NamedTuple, Iterable

from shapely.geometry import Polygon

from common_image.model.ndimagedata import NdImageData
from slice.model.patch_pos import PatchPos
from slice.model.patch_image_config import PatchImageConfig


class PatchResponse(NamedTuple):
    pos: PatchPos
    polygon: Polygon
    img: NdImageData
    cfg: PatchImageConfig


PatchResponseIterable = Iterable[PatchResponse]