import skimage
import skimage.color
import skimage.measure

from annotation.model import AnnotationModel
from annotation_image.core import build_region_data, read_masked_region
from annotation_image.reagion_data import RegionData
from common.timeit_utils import timing
from common_htk.nuclei import ndimg_to_nuclei_seg_mask
from common_image.model.ndimg import Ndimg
from common_image_qt.core import ndimg_to_qimg
from filter.common.filter_output import FilterOutput
from filter.common.filter_results import FilterResults
from filter.nuclei.nuclei_filter_model import NucleiParams, NucleiFilterData


def nuclei_filter(annotation: AnnotationModel, filter_data: NucleiFilterData,
				  img_path: str) -> FilterOutput:
	rd = build_region_data(img_path, annotation, annotation.filter_level)
	results = _nuclei_filter(rd, filter_data.nuclei_params)
	return results


# @gcached
@timing
def _nuclei_filter(rd: RegionData, params: NucleiParams) -> FilterOutput:
	ndimg = read_masked_region(rd)
	seg_mask = ndimg_to_nuclei_seg_mask(ndimg, params)
	region_props = skimage.measure.regionprops(seg_mask.ndarray)
	labeled_ndimg = skimage.color.label2rgb(seg_mask.ndarray, ndimg.ndarray, bg_label=0)
	labeled_ndimg = skimage.util.img_as_ubyte(labeled_ndimg, force_copy=True)
	qimg = ndimg_to_qimg(Ndimg(labeled_ndimg, "RGB", ndimg.bool_mask_ndarray))
	nuclei_count = len(region_props)
	dict_ = {'nuclei_count': nuclei_count}
	results = FilterResults(f"nuclei count: {nuclei_count}", dict_)
	return FilterOutput(qimg, ndimg.bool_mask_ndarray, results)
