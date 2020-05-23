from dataclasses import asdict

from common.dict_utils import remove_none_values
from common.timeit_utils import timing
from common_image.core.hist import ndimg_to_hist
from common_image.core.hist_html import build_histogram_html
from common_image.core.kmeans import ndimg_to_quantized_ndimg
from common_image_qt.core import ndimg_to_qimg
from img.filter.kmeans_filter import KMeansFilterData, KMeansFilterResults, KMeansParams
from img.filter.threshold_filter import ThresholdFilterResults
from img.proc.region import RegionData
from slide_viewer.ui.common.model import AnnotationModel
from slide_viewer.ui.slide.widget.filter.region_data import build_region_data, read_masked_region


def kmeans_filter(annotation: AnnotationModel, filter_data: KMeansFilterData,
				  img_path: str) -> KMeansFilterResults:
	rd = build_region_data(img_path, annotation, annotation.filter_level)
	results = _kmeans_filter(rd, filter_data.kmeans_params)
	return results

@timing
def _kmeans_filter(rd: RegionData, params: KMeansParams) -> KMeansFilterResults:
	ndimg = read_masked_region(rd)
	# img_to_kmeans_quantized_img_ = closure_nonhashable(hashkey(rd), ndimg, img_to_kmeans_quantized_img)
	kwargs = remove_none_values(asdict(params))
	kwargs['init'] = params.init.value
	quantized_ndimg = timing(ndimg_to_quantized_ndimg)(ndimg, **kwargs)
	# quantized_ndimg = img_to_kmeans_quantized_img_(params)
	hist = ndimg_to_hist(quantized_ndimg)
	hist_html = build_histogram_html(hist.sorted_most_freq_colors, hist.sorted_most_freq_colors_counts)
	qimg = ndimg_to_qimg(quantized_ndimg)
	res = KMeansFilterResults(qimg, ndimg.bool_mask_ndarray, hist_html)
	return res
