from dataclasses import asdict

from annotation.model import AnnotationModel
from annotation_image.core import build_region_data, read_masked_region
from annotation_image.reagion_data import RegionData
from common.dict_utils import remove_none_values
from common.timeit_utils import timing
from common_image.core.hist import ndimg_to_hist
from common_image.core.hist_html import build_histogram_html, build_hist_dict
from common_image.core.kmeans import ndimg_to_quantized_ndimg
from common_image_qt.core import ndimg_to_qimg
from filter.common.filter_model import FilterOutput, FilterResults
from filter.kmeans.kmeans_filter_model import KMeansParams, KMeansFilterData


def kmeans_filter(annotation: AnnotationModel, filter_data: KMeansFilterData,
				  img_path: str) -> FilterOutput:
	rd = build_region_data(img_path, annotation, annotation.filter_level)
	results = _kmeans_filter(rd, filter_data.kmeans_params)
	return results


@timing
def _kmeans_filter(rd: RegionData, params: KMeansParams) -> FilterOutput:
	ndimg = read_masked_region(rd)
	# img_to_kmeans_quantized_img_ = closure_nonhashable(hashkey(rd), ndimg, img_to_kmeans_quantized_img)
	kwargs = remove_none_values(asdict(params))
	kwargs['init'] = params.init.value
	quantized_ndimg = ndimg_to_quantized_ndimg(ndimg, **kwargs)
	# quantized_ndimg = img_to_kmeans_quantized_img_(params)
	hist = ndimg_to_hist(quantized_ndimg)
	hist_html = build_histogram_html(hist.sorted_most_freq_colors, hist.sorted_most_freq_colors_counts)
	hist_dict = build_hist_dict(hist.sorted_most_freq_colors, hist.sorted_most_freq_colors_counts)
	qimg = ndimg_to_qimg(quantized_ndimg)
	results = FilterResults(hist_html, {'histogram': hist_dict})
	output = FilterOutput(qimg, ndimg.bool_mask_ndarray, results)
	return output
