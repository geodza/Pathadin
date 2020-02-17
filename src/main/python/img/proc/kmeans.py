from enum import unique, Enum
from typing import Union

import numpy as np
from dataclasses import dataclass, field

from common.dataclass_utils import dataclass_fields


@unique
class KMeansInitType(Enum):
    kmeansPlusPlus = 'k-means++'
    random = 'random'
    ndarray = 'use NdarrayKMeansParams.ndarray to specify ndarray as start centroid centers'


@dataclass(frozen=True)
class KMeansParams:
    n_clusters: int = 3
    init: KMeansInitType = KMeansInitType.kmeansPlusPlus
    n_init: int = 5
    max_iter: int = 50
    tol: float = 1e-1
    precompute_distances: Union[str, bool] = 'auto'
    random_state: int = None


@dataclass_fields
class KMeansParams_(KMeansParams):
    pass


# TODO make hashable with tuple points
@dataclass(frozen=True)
class NdarrayKMeansParams(KMeansParams):
    ndarray: np.ndarray = field(default_factory=np.array)


@dataclass_fields
class NdarrayKMeansParams_(NdarrayKMeansParams):
    pass


