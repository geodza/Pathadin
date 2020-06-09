import histomicstk as htk
import numpy as np
from dataclasses import asdict
from scipy import ndimage

from common_image.model.ndimg import Ndimg
from filter.nuclei.nuclei_filter_model import default_stain_color_map, NucleiParams


def ndimg_to_nuclei_seg_mask(ndimg: Ndimg, params: NucleiParams) -> Ndimg:
    nuclei_seg_mask = ndarray_to_nuclei_seg_mask(ndimg.ndarray, params)
    return Ndimg(nuclei_seg_mask, "L", ndimg.bool_mask_ndarray)


def ndarray_to_nuclei_seg_mask(ndarray: np.ndarray, params: NucleiParams) -> np.ndarray:
    if len(ndarray.shape) != 3 or ndarray.shape[2] > 4 or ndarray.shape[2] < 3:
        raise ValueError(f"Unsupported img shape: {ndarray.shape}")
    nuclei_seg_mask = build_nuclei_seg_mask(ndarray, **asdict(params))
    return nuclei_seg_mask


def build_nuclei_seg_mask(im_reference: np.ndarray, foreground_threshold=60, min_radius=10,
                          max_radius=15, local_max_search_radius=10.0, min_nucleus_area=80,
                          stain_color_map=default_stain_color_map(),
                          stain_1='hematoxylin', stain_2='eosin', stain_3='null') -> np.ndarray:
    im_reference = im_reference[:, :, :3]
    mean_ref, std_ref = htk.preprocessing.color_conversion.lab_mean_std(im_reference)
    im_nmzd = htk.preprocessing.color_normalization.reinhard(im_reference, mean_ref, std_ref)
    # create stain matrix
    W = np.array([stain_color_map[stain_1],
                  stain_color_map[stain_2],
                  stain_color_map[stain_3]]).T
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
