from annotation.model import AnnotationModel
from annotation_image.core import build_region_data, read_masked_region
from annotation_image.reagion_data import RegionData
from common.timeit_utils import timing
from common_image.core.mode_convert import convert_ndimg
from filter.common.filter_output import FilterOutput
from filter.common.threshold_filter import threshold_filter
from filter.manual_threshold.manual_threshold_filter_model import GrayManualThresholdFilterData, \
	HSVManualThresholdFilterData


@timing
def manual_threshold_filter(rd: RegionData, color_mode: str, threshold_range: tuple) -> FilterOutput:
	ndimg = read_masked_region(rd)
	# converted_ndimg = closure_nonhashable(hashkey(rd), ndimg, convert_ndimg)(color_mode)
	converted_ndimg = convert_ndimg(ndimg, color_mode)
	return threshold_filter(converted_ndimg, threshold_range)


def gray_manual_threshold_filter(annotation: AnnotationModel, filter_data: GrayManualThresholdFilterData,
								 img_path: str) -> FilterOutput:
	rd = build_region_data(img_path, annotation, annotation.filter_level)
	results = manual_threshold_filter(rd, 'L', filter_data.gray_range)
	return results


def hsv_manual_threshold_filter(annotation: AnnotationModel, filter_data: HSVManualThresholdFilterData,
								img_path: str) -> FilterOutput:
	rd = build_region_data(img_path, annotation, annotation.filter_level)
	results = manual_threshold_filter(rd, 'HSV', filter_data.hsv_range)
	return results
