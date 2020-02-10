from typing import Optional

import numpy as np
from dataclasses import dataclass

from img.ndimagedata import NdImageData


@dataclass(frozen=True)
class HistParams:
    k: Optional[int] = None
    normed: bool = True


@dataclass
class HistResults:
    sorted_most_freq_colors: np.ndarray
    sorted_most_freq_colors_counts: np.ndarray


def ndimg_to_hist(params: HistParams, img: NdImageData) -> HistResults:
    foreground_color_points = img.ndimg[img.bool_mask_ndimg]
    # ndimg = img.ndimg
    # if ndimg.ndim == 3:
    #     color_arrays = ndimg.reshape(-1, ndimg.shape[-1])
    # else:
    #     color_arrays = ndimg.reshape(-1)
    unique_colors, unique_counts = np.unique(foreground_color_points, return_counts=True, axis=0)
    # k = 5 if len(unique_counts) > 5 else 0
    k = min(params.k, len(unique_counts)) if params.k is not None else len(unique_counts)
    # print(f"k: {k} unique_counts: {unique_counts}")
    most_freq_colors_indices = np.argpartition(unique_counts, len(unique_counts) - k - 1)[-k:]
    sorted_most_freq_colors_indices = most_freq_colors_indices[np.argsort(unique_counts[most_freq_colors_indices])]
    sorted_most_freq_colors_indices = sorted_most_freq_colors_indices[::-1]
    sorted_most_freq_colors = unique_colors[sorted_most_freq_colors_indices]
    sorted_most_freq_colors_counts = unique_counts[sorted_most_freq_colors_indices]
    if params.normed:
        return HistResults(sorted_most_freq_colors, sorted_most_freq_colors_counts / np.sum(
            sorted_most_freq_colors_counts))
    else:
        return HistResults(sorted_most_freq_colors, sorted_most_freq_colors_counts)
