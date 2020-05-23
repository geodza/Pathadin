from cachetools.keys import hashkey
from dataclasses import asdict

from common.dict_utils import remove_none_values
from common_image.core.mode_convert import convert_ndimg
from common_image.core.skimage_threshold import find_ndimg_skimage_threshold
from filter.manual_threshold.manual_threshold_filter import threshold_filter
from img.filter.skimage_threshold import SkimageAutoThresholdFilterData, SkimageMinimumThresholdFilterData, \
	SkimageThresholdParams, SkimageMeanThresholdFilterData
from img.filter.threshold_filter import ThresholdFilterResults
from img.proc.region import RegionData
from slide_viewer.cache_config import closure_nonhashable, gcached
from slide_viewer.ui.common.model import AnnotationModel
from slide_viewer.ui.slide.widget.filter.region_data import build_region_data, read_masked_region


def skimage_threshold_filter(annotation: AnnotationModel, filter_data: SkimageAutoThresholdFilterData,
							 img_path: str) -> ThresholdFilterResults:
	rd = build_region_data(img_path, annotation, annotation.filter_level)
	if isinstance(filter_data, SkimageMinimumThresholdFilterData):
		params = SkimageThresholdParams(filter_data.skimage_threshold_type,
										filter_data.skimage_threshold_minimum_params)
	elif isinstance(filter_data, SkimageMeanThresholdFilterData):
		params = SkimageThresholdParams(filter_data.skimage_threshold_type, None)
	else:
		raise ValueError()

	results = _skimage_threshold_filter(rd, params)
	return results


@gcached
def _skimage_threshold_filter(rd: RegionData, params: SkimageThresholdParams):
	ndimg = read_masked_region(rd)
	converted_ndimg = closure_nonhashable(hashkey(rd), ndimg, convert_ndimg)("L")
	kwargs = remove_none_values(asdict(params.params)) if params.params else {}
	# return ndimg_to_skimage_thresholded_ndimg(img.ndarray, params.type.name, **kwargs)
	threshold = find_ndimg_skimage_threshold(converted_ndimg, params.type.name, **kwargs)
	threshold_range = (0, threshold)
	# threshold_range = ndimg_to_skimage_threshold_range(params, converted_ndimg)
	return threshold_filter(converted_ndimg, threshold_range)
