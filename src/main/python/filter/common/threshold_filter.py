from common.timeit_utils import timing
from common_image.core.hist import ndimg_to_hist
from common_image.core.hist_html import build_histogram_html, build_hist_dict
from common_image.core.threshold import ndimg_to_thresholded_ndimg
from common_image.model.ndimg import Ndimg
from common_image_qt.core import ndimg_to_qimg
from filter.common.filter_output import FilterOutput
from filter.common.filter_results import FilterResults


@timing
def threshold_filter(img: Ndimg, threshold_range: tuple) -> FilterOutput:
	thresholded_ndimg = ndimg_to_thresholded_ndimg(img, threshold_range)
	hist = ndimg_to_hist(thresholded_ndimg)
	hist_html = build_histogram_html(hist.sorted_most_freq_colors, hist.sorted_most_freq_colors_counts)
	hist_dict = build_hist_dict(hist.sorted_most_freq_colors, hist.sorted_most_freq_colors_counts)
	qimg = ndimg_to_qimg(thresholded_ndimg)
	results = FilterResults(hist_html, {'histogram': hist_dict})
	output = FilterOutput(qimg, thresholded_ndimg.bool_mask_ndarray, results)
	return output
