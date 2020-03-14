from enum import unique, Enum, auto
from typing import Optional

import numpy as np
from PyQt5.QtGui import QImage
from dataclasses import dataclass, field

from common.dataclass_utils import dataclass_fields


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
    realtime: bool = True


@dataclass_fields
class FilterData_(FilterData):
    pass


@dataclass
class FilterResults2:
    img: QImage
    bool_mask_ndimg: Optional[np.ndarray]

# @dataclass()
# class NucleiFilterResults(FilterResults):
#     n_nuclei: int
