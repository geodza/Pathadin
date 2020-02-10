import typing
from enum import unique, Enum

import numpy as np
from dataclasses import dataclass, field, asdict
from sklearn.cluster import KMeans

from img.ndimagedata import NdImageData
from slide_viewer.common.dataclass_utils import dataclass_fields
from slide_viewer.common.dict_utils import remove_none_values


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
    precompute_distances: typing.Union[str, bool] = 'auto'
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


def img_to_kmeans_quantized_img(img: NdImageData, params: KMeansParams) -> NdImageData:
    foreground_color_points = img.ndimg[img.bool_mask_ndimg]
    # ndimg = ma.array(img.ndimg, mask=img.mask_ndimg)
    # foreground_color_points = ndimg.compressed.reshape((-1, img.ndimg.shape[-1]))
    # foreground_color_points = ndimg.reshape((-1, ndimg.shape[-1]))
    kwargs = remove_none_values(asdict(params))
    kwargs['init'] = params.init.value
    if kwargs['n_clusters'] > len(foreground_color_points):
        kwargs['n_clusters'] = len(foreground_color_points)
    kmeans = KMeans(**kwargs)
    kmeans.fit(foreground_color_points)
    color_points = img.ndimg.reshape((-1, img.ndimg.shape[-1]))
    labels = kmeans.predict(color_points)
    centers = kmeans.cluster_centers_.astype(np.uint8)
    color_points_quantized = centers[labels]
    ndimg_quantized = color_points_quantized.reshape(img.ndimg.shape)
    img_quantized = NdImageData(ndimg_quantized, img.color_mode, img.bool_mask_ndimg)
    return img_quantized

# def img_to_kmeans_quantized_img_centrois(params: KMeansParams, img: NdImageData) -> NdImageData:
