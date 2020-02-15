from dataclasses import dataclass
from img.ndimagedata import NdImageData
from common.dataclass_utils import dataclass_fields


@dataclass
class KerasModelResults:
    labeled_img: NdImageData
    region_props: list


@dataclass(frozen=True)
class KerasModelParams():
    model_path: str

@dataclass_fields
class KerasModelParams_(KerasModelParams):
    pass

