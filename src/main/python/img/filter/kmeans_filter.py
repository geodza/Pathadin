from enum import unique, Enum
from typing import Union

import numpy as np
from dataclasses import dataclass, field

from common.dataclass_utils import dataclass_fields
from img.filter.base_filter import FilterData, FilterType, FilterResults2


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


@dataclass(frozen=True)
class KMeansFilterData(FilterData):
    filter_type: FilterType = field(default=FilterType.KMEANS, init=False)
    kmeans_params: KMeansParams = field(default_factory=KMeansParams)


@dataclass_fields
class KMeansFilterData_(KMeansFilterData):
    pass


@dataclass
class KMeansFilterResults(FilterResults2):
    histogram_html: str


# @dataclass(frozen=True)
# class NdarrayKMeansParams(KMeansParams):
#     # TODO make hashable with tuple points
#     ndarray: np.ndarray = field(default_factory=np.array)
#
#
# @dataclass_fields
# class NdarrayKMeansParams_(NdarrayKMeansParams):
#     pass
