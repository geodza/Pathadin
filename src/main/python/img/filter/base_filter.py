from enum import unique, Enum, auto
from typing import Union, Dict, Optional

import numpy as np
from PIL import Image
from PyQt5.QtGui import QImage
from dataclasses import dataclass, field

from slide_viewer.common.dataclass_utils import dataclass_fields


@unique
class FilterType(Enum):
    THRESHOLD = auto()
    KMEANS = auto()
    NUCLEI = auto()
    POSITIVE_PIXEL_COUNT = auto()
    KERAS_MODEL = auto()


@dataclass(frozen=True)
class FilterData:
    id: str
    filter_type: FilterType = field(init=False)


@dataclass_fields
class FilterData_(FilterData):
    pass


Img = Union[Image.Image, np.ndarray, QImage]


@dataclass()
class FilterResults:
    img: Img
    color_mode: str
    filter_type: Optional[FilterType]
    metadata: Dict[str, any] = field(default_factory=dict)


@dataclass_fields
class FilterResults_(FilterResults):
    pass


@dataclass
class FilterResults2:
    img: QImage
    bool_mask_ndimg: Optional[np.ndarray]


@dataclass
class ThresholdFilterResults(FilterResults2):
    histogram_html: str

# @dataclass()
# class NucleiFilterResults(FilterResults):
#     n_nuclei: int
