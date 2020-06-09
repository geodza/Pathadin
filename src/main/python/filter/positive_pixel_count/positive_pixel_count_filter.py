from typing import Tuple

import skimage.color
import skimage.util
from cachetools.keys import hashkey
from dataclasses import asdict
from histomicstk.segmentation import positive_pixel_count as ppc

from common.timeit_utils import timing
from common_image.core.mode_convert import convert_ndimg
from common_image.model.ndimg import Ndimg
from common_image_qt.core import ndimg_to_qimg
from filter.common.filter_model import FilterResults, FilterOutput
from filter.positive_pixel_count.positive_pixel_count_filter_model import PositivePixelCountParams, \
	PositivePixelCountFilterData
from annotation_image.reagion_data import RegionData
from slide_viewer.cache_config import closure_nonhashable
from annotation.model import AnnotationModel
from annotation_image.core import build_region_data, read_masked_region


def positive_pixel_count_filter(annotation: AnnotationModel, filter_data: PositivePixelCountFilterData,
								img_path: str) -> FilterOutput:
	rd = build_region_data(img_path, annotation, annotation.filter_level)
	results = _positive_pixel_count_filter(rd, filter_data.positive_pixel_count_params)
	return results


@timing
def _positive_pixel_count_filter(rd: RegionData, params: PositivePixelCountParams) -> FilterOutput:
	ndimg = read_masked_region(rd)
	converted_ndimg = closure_nonhashable(hashkey(rd), ndimg, convert_ndimg)("RGB")
	ndimg, stats = positive_pixel_count2(converted_ndimg, params)
	qimg = ndimg_to_qimg(ndimg)
	try:
		stats_dict = stats._asdict()
		stats_html_text = '<br/>'.join([f'{k}: {round(v, 3)}' for k, v in stats_dict.items()])
		# filter_results_dict = {'stats_html_text': stats_html_text}
		results = FilterResults(stats_html_text, {'ppc_output':stats_dict})
	except:
		stats_dict = stats._asdict()
		# filter_results_dict = {'stats_html_text': "error, try to move annotation or to change filter params"}
		results = FilterResults("error, try to move annotation or to change filter params", stats_dict)
	res = FilterOutput(qimg, ndimg.bool_mask_ndarray, results)
	return res


def positive_pixel_count2(img: Ndimg, params: PositivePixelCountParams) -> Tuple[Ndimg, ppc.Output]:
	stats, label_image = ppc.count_image(img.ndarray, ppc.Parameters(**asdict(params)))
	colors = [(0, 0, 0), (0.5, 0.5, 0.5), (0.75, 0.75, 0.75), (1, 1, 1)]
	labeled_ndimg = skimage.color.label2rgb(label_image, colors=colors, bg_label=0)
	labeled_ndimg = skimage.util.img_as_ubyte(labeled_ndimg, force_copy=True)
	return (Ndimg(labeled_ndimg, "RGB", img.bool_mask_ndarray), stats)
