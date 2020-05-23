from cachetools.keys import hashkey

from common.timeit_utils import timing
from common_image.core.hist import ndimg_to_hist
from common_image.core.hist_html import build_histogram_html
from common_image.core.mode_convert import convert_ndimg
from common_image.core.threshold import ndimg_to_thresholded_ndimg
from common_image.model.ndimg import Ndimg
from common_image_qt.core import ndimg_to_qimg
from img.filter.manual_threshold import HSVManualThresholdFilterData, GrayManualThresholdFilterData
from img.filter.threshold_filter import ThresholdFilterResults
from img.proc.region import RegionData
from slide_viewer.cache_config import gcached, closure_nonhashable
from slide_viewer.ui.common.model import AnnotationModel
from slide_viewer.ui.slide.widget.filter.region_data import build_region_data, read_masked_region

@timing
def threshold_filter(img: Ndimg, threshold_range: tuple) -> ThresholdFilterResults:
	thresholded_ndimg = ndimg_to_thresholded_ndimg(img, threshold_range)
	hist = ndimg_to_hist(thresholded_ndimg)
	hist_html = build_histogram_html(hist.sorted_most_freq_colors, hist.sorted_most_freq_colors_counts)
	qimg = ndimg_to_qimg(thresholded_ndimg)
	res = ThresholdFilterResults(qimg, thresholded_ndimg.bool_mask_ndarray, hist_html)
	return res

@timing
def manual_threshold_filter(rd: RegionData, color_mode: str, threshold_range: tuple) -> ThresholdFilterResults:
	ndimg = read_masked_region(rd)
	# converted_ndimg = closure_nonhashable(hashkey(rd), ndimg, convert_ndimg)(color_mode)
	converted_ndimg = convert_ndimg(ndimg, color_mode)
	return threshold_filter(converted_ndimg, threshold_range)


def gray_manual_threshold_filter(annotation: AnnotationModel, filter_data: GrayManualThresholdFilterData,
								 img_path: str) -> ThresholdFilterResults:
	rd = build_region_data(img_path, annotation, annotation.filter_level)
	results = manual_threshold_filter(rd, 'L', filter_data.gray_range)
	return results


def hsv_manual_threshold_filter(annotation: AnnotationModel, filter_data: HSVManualThresholdFilterData,
								img_path: str) -> ThresholdFilterResults:
	rd = build_region_data(img_path, annotation, annotation.filter_level)
	results = manual_threshold_filter(rd, 'HSV', filter_data.hsv_range)
	return results
