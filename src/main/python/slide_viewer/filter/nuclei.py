import histomicstk as htk
import numpy as np
import skimage.color
import skimage.io
import skimage.measure
import skimage.util
from PIL import Image
from scipy import ndimage

from slide_viewer.ui.common.img.img_object_convert import expose_pilimage_buffer_to_ndarray
from slide_viewer.ui.model.filter.base_filter import FilterResults
from slide_viewer.ui.model.filter.nuclei import NucleiFilterData

stainColorMap = {
    'hematoxylin': [0.65, 0.70, 0.29],
    'eosin': [0.07, 0.99, 0.11],
    'dab': [0.27, 0.57, 0.78],
    'null': [0.0, 0.0, 0.0]
}

# specify stains of input image
stain_1 = 'hematoxylin'  # nuclei stain
stain_2 = 'eosin'  # cytoplasm stain
stain_3 = 'null'  # set to null of input contains only two stains


def build_nuclei_seg_mask(im_reference: np.ndarray, foreground_threshold=60, min_radius=10,
                          max_radius=15, local_max_search_radius=10.0, min_nucleus_area=80) -> np.ndarray:
    mean_ref, std_ref = htk.preprocessing.color_conversion.lab_mean_std(im_reference)
    im_nmzd = htk.preprocessing.color_normalization.reinhard(im_reference, mean_ref, std_ref)
    # create stain matrix
    W = np.array([stainColorMap[stain_1],
                  stainColorMap[stain_2],
                  stainColorMap[stain_3]]).T
    # np.array(list(stainColorMap.values()))[[0,1,3]].T
    im_stains = htk.preprocessing.color_deconvolution.color_deconvolution(im_nmzd, W).Stains
    im_nuclei_stain = im_stains[:, :, 0]

    im_fgnd_mask = ndimage.morphology.binary_fill_holes(
        im_nuclei_stain < foreground_threshold)

    im_log_max, im_sigma_max = htk.filters.shape.cdog(
        im_nuclei_stain, im_fgnd_mask,
        sigma_min=min_radius * np.sqrt(2),
        sigma_max=max_radius * np.sqrt(2)
    )
    # detect and segment nuclei using local maximum clustering

    # local_max_search_radius = np.array([10], dtype=np.int32)[0]
    im_nuclei_seg_mask, seeds, maxima = htk.segmentation.nuclear.max_clustering(
        im_log_max, im_fgnd_mask, local_max_search_radius)

    # filter out small objects

    im_nuclei_seg_mask = htk.segmentation.label.area_open(
        im_nuclei_seg_mask, min_nucleus_area).astype(np.int)

    # objProps = skimage.measure.regionprops(im_nuclei_seg_mask)
    # print('Number of nuclei = ', len(objProps))
    return im_nuclei_seg_mask


# @gcached("nuclei_filter")
def process_nuclei_filter(fr: FilterResults, filter_data: NucleiFilterData) -> FilterResults:
    if isinstance(fr.img, Image.Image):
        fr.color_mode = fr.img.mode
        fr.img = expose_pilimage_buffer_to_ndarray(fr.img)
    elif isinstance(fr.img, np.ndarray):
        pass
    else:
        raise ValueError(f"Unsupported img type for process_nuclei_filter: {fr.img}")
    ndimg = fr.img
    ndimg = ndimg[:, :, :3]
    nuclei_seg_mask = build_nuclei_seg_mask(ndimg, filter_data.nuclei_params.foreground_threshold,
                                            filter_data.nuclei_params.min_radius, filter_data.nuclei_params.max_radius,
                                            filter_data.nuclei_params.local_max_search_radius,
                                            filter_data.nuclei_params.min_nucleus_area)
    objProps = skimage.measure.regionprops(nuclei_seg_mask)
    nuclei_results = {
        'nuclei_count', len(objProps)
    }
    labeled_ndimg = skimage.color.label2rgb(nuclei_seg_mask, ndimg, bg_label=0)
    labeled_ndimg = skimage.util.img_as_ubyte(labeled_ndimg, force_copy=True)
    fr.color_mode = "RGB"
    fr.img = labeled_ndimg
    # fr.metadata = fr.metadata or {}
    fr.metadata['nuclei_count'] = len(objProps)
    return fr
    # return expose_ndarray_buffer_to_pillowimage(labeled_ndimg, "RGB")
