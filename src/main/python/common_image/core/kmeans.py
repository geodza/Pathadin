from typing import Optional

import numpy as np
from sklearn.cluster import KMeans

from common_image.model.ndimg import Ndimg


def ndimg_to_quantized_ndimg(ndimg: Ndimg, **kwargs) -> Ndimg:
    fit_ndarray = ndimg.ndarray[ndimg.bool_mask_ndarray] if ndimg.bool_mask_ndarray is not None else ndimg.ndarray
    predict_ndarray = ndimg.ndarray
    predict_ndarray_quantized = ndarray_to_quantized_ndarray(fit_ndarray, predict_ndarray, **kwargs)
    return Ndimg(predict_ndarray_quantized, ndimg.color_mode, ndimg.bool_mask_ndarray)


def ndarray_to_quantized_ndarray(fit_ndarray: np.ndarray, predict_ndarray: Optional[np.ndarray] = None, **kwargs) -> np.ndarray:
    # https://scikit-learn.org/stable/modules/generated/sklearn.cluster.KMeans.html
    fit_color_points = fit_ndarray.reshape((-1, fit_ndarray.shape[-1]))
    kwargs_ = dict(kwargs)
    if kwargs_['n_clusters'] > len(fit_color_points):
        kwargs_['n_clusters'] = len(fit_color_points)
    kmeans = KMeans(**kwargs_)
    kmeans.fit(fit_color_points)

    predict_ndarray = predict_ndarray if predict_ndarray is not None else fit_ndarray
    predict_color_points = predict_ndarray.reshape((-1, predict_ndarray.shape[-1]))
    labels = kmeans.predict(predict_color_points)
    centers = kmeans.cluster_centers_.astype(np.uint8)
    predict_color_points_quantized = centers[labels]
    predict_ndarray_quantized = predict_color_points_quantized.reshape(predict_ndarray.shape)
    return predict_ndarray_quantized
