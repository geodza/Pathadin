from dataclasses import dataclass, asdict
from img.ndimagedata import NdImageData
from slide_viewer.cache_config import gcached
from slide_viewer.common.dataclass_utils import dataclass_fields


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

