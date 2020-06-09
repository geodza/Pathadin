from cachetools.keys import hashkey
from dataclasses import asdict

from common.dict_utils import remove_none_values
from common_image.core.mode_convert import convert_ndimg
from common_image.core.skimage_threshold import find_ndimg_skimage_threshold
from filter.common.filter_model import FilterOutput
from filter.common.threshold_filter import threshold_filter
from filter.skimage_threshold.skimage_threshold_filter_model import SkimageThresholdFilterData, \
	SkimageMinimumThresholdFilterData, \
	SkimageThresholdParams, SkimageMeanThresholdFilterData
from annotation_image.reagion_data import RegionData
from slide_viewer.cache_config import closure_nonhashable, gcached
from annotation.model import AnnotationModel
from annotation_image.core import build_region_data, read_masked_region


def skimage_threshold_filter(annotation: AnnotationModel, filter_data: SkimageThresholdFilterData,
							 img_path: str) -> FilterOutput:
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
def _skimage_threshold_filter(rd: RegionData, params: SkimageThresholdParams) -> FilterOutput:
	ndimg = read_masked_region(rd)
	converted_ndimg = closure_nonhashable(hashkey(rd), ndimg, convert_ndimg)("L")
	kwargs = remove_none_values(asdict(params.params)) if params.params else {}
	# return ndimg_to_skimage_thresholded_ndimg(img.ndarray, params.type.name, **kwargs)
	threshold = find_ndimg_skimage_threshold(converted_ndimg, params.type.name, **kwargs)
	threshold_range = (0, threshold)
	# threshold_range = ndimg_to_skimage_threshold_range(params, converted_ndimg)
	return threshold_filter(converted_ndimg, threshold_range)
