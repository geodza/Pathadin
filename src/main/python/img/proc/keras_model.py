from dataclasses import dataclass
from common_image.model.ndimg import Ndimg
from common.dataclass_utils import dataclass_fields


@dataclass
class KerasModelResults:
    labeled_img: Ndimg
    region_props: list


@dataclass(frozen=True)
class KerasModelParams():
    model_path: str

@dataclass_fields
class KerasModelParams_(KerasModelParams):
    pass

