from cachetools.keys import hashkey
from common.timeit_utils import timing
from common_image.core.mode_convert import convert_ndimg
from common_image_qt.core import ndimg_to_qimg
from img.filter.positive_pixel_count import positive_pixel_count2, PositivePixelCountParams, \
	PositivePixelCountFilterResults, PositivePixelCountFilterData
from img.proc.region import RegionData
from slide_viewer.cache_config import closure_nonhashable
from slide_viewer.ui.common.model import AnnotationModel
from slide_viewer.ui.slide.widget.filter.region_data import build_region_data, read_masked_region


def positive_pixel_count_filter(annotation: AnnotationModel, filter_data: PositivePixelCountFilterData,
								img_path: str) -> PositivePixelCountFilterResults:
	rd = build_region_data(img_path, annotation, annotation.filter_level)
	results = _positive_pixel_count_filter(rd, filter_data.positive_pixel_count_params)
	return results


@timing
def _positive_pixel_count_filter(rd: RegionData, params: PositivePixelCountParams) -> PositivePixelCountFilterResults:
	ndimg = read_masked_region(rd)
	converted_ndimg = closure_nonhashable(hashkey(rd), ndimg, convert_ndimg)("RGB")
	ndimg, stats = positive_pixel_count2(converted_ndimg, params)
	qimg = ndimg_to_qimg(ndimg)
	res = PositivePixelCountFilterResults(qimg, ndimg.bool_mask_ndarray, stats)
	return res
