import openslide
import skimage
from dataclasses import asdict
from shapely.affinity import translate
from shapely.geometry import box

from common.dict_utils import remove_none_values
from common.grid_utils import pos_range
from common.timeit_utils import timing
from common_htk.nuclei import ndimg_to_nuclei_seg_mask
from common_image.model.ndimg import Ndimg
from common_image_qt.core import ndimg_to_qimg
from img.filter.nuclei import NucleiParams, NucleiFilterResults, NucleiFilterData
from img.proc.region import RegionData
from slide_viewer.ui.common.model import AnnotationModel, AnnotationGeometry
from slide_viewer.ui.slide.widget.filter.region_data import build_region_data, read_masked_region
import skimage.measure, skimage.color


def nuclei_filter(annotation: AnnotationModel, filter_data: NucleiFilterData,
				  img_path: str) -> NucleiFilterResults:
	rd = build_region_data(img_path, annotation, annotation.filter_level)
	results = _nuclei_filter(rd, filter_data.nuclei_params)
	return results


# @gcached
@timing
def _nuclei_filter(rd: RegionData, params: NucleiParams) -> NucleiFilterResults:
	ndimg = read_masked_region(rd)
	seg_mask = ndimg_to_nuclei_seg_mask(ndimg, params)
	region_props = skimage.measure.regionprops(seg_mask.ndarray)
	labeled_ndimg = skimage.color.label2rgb(seg_mask.ndarray, ndimg.ndarray, bg_label=0)
	labeled_ndimg = skimage.util.img_as_ubyte(labeled_ndimg, force_copy=True)
	qimg = ndimg_to_qimg(Ndimg(labeled_ndimg, "RGB", ndimg.bool_mask_ndarray))
	return NucleiFilterResults(qimg, ndimg.bool_mask_ndarray, len(region_props))
