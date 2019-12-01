import numpy as np
from PIL import Image
from dataclasses import asdict
from sklearn.cluster import KMeans

from slide_viewer.common.dict_utils import remove_none_values
from slide_viewer.ui.common.img.img_object_convert import expose_pilimage_buffer_to_ndarray
from slide_viewer.ui.model.filter.base_filter import FilterResults
from slide_viewer.ui.model.filter.kmeans_filter import KMeansFilterData, NdarrayKMeansParams
from slide_viewer.ui.slide.widget.histogram_builder import build_histogram_html_for_ndimg


def process_kmeans_filter(fr: FilterResults, filter_data: KMeansFilterData) -> FilterResults:
    if isinstance(fr.img, Image.Image):
        fr.color_mode = fr.img.mode
        fr.img = expose_pilimage_buffer_to_ndarray(fr.img)
    elif isinstance(fr.img, np.ndarray):
        pass
    else:
        raise ValueError(f"Unsupported img type for process_kmeans_filter: {fr.img}")

    fr.img = process_kmeans_filter_ndimg(fr.img, filter_data)

    histogram_html = build_histogram_html_for_ndimg(fr.img)
    fr.metadata['normed_hist'] = histogram_html
    # fr.color_mode='RGBA'

    # pilimg_quantized = expose_ndarray_buffer_to_pillowimage(ndimg_quantized, img.mode)
    return fr


def process_kmeans_filter_ndimg(ndimg: np.ndarray, filter_data: KMeansFilterData) -> np.ndarray:
    color_points = ndimg.reshape((-1, ndimg.shape[-1]))
    if isinstance(filter_data.kmeans_params, NdarrayKMeansParams):
        pass
    else:
        kwargs = remove_none_values(asdict(filter_data.kmeans_params))
        kwargs['init'] = filter_data.kmeans_params.init.value
        if kwargs['n_clusters'] > len(color_points):
            kwargs['n_clusters'] = len(color_points)
        kmeans = KMeans(**kwargs)
        labels = kmeans.fit_predict(color_points)
        centers = kmeans.cluster_centers_.astype(np.uint8)
        color_points_quantized = centers[labels]
        ndimg_quantized = color_points_quantized.reshape(ndimg.shape)

        return ndimg_quantized
    return np.array([])
