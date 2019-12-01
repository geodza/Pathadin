import numpy as np
from dataclasses import asdict

from slide_viewer.common.dict_utils import remove_none_values, narrow_dict
from slide_viewer.ui.model.filter.threshold_filter import SkimageAutoThresholdFilterData, \
    SkimageMeanThresholdFilterData, SkimageMinimumThresholdFilterData, SkimageMinimumThresholdFilterData_


# @gcached("skimage_threshold")
def skimage_threshold(img: np.ndarray, filter_data: SkimageAutoThresholdFilterData) -> float:
    if isinstance(filter_data, SkimageMeanThresholdFilterData):
        from skimage.filters import threshold_mean
        return threshold_mean(img)
    elif isinstance(filter_data, SkimageMinimumThresholdFilterData):
        from skimage.filters import threshold_minimum
        kwargs = remove_none_values(narrow_dict(asdict(filter_data),
                                                [SkimageMinimumThresholdFilterData_.nbins,
                                                 SkimageMinimumThresholdFilterData_.max_iter]))
        return threshold_minimum(img, **kwargs)
