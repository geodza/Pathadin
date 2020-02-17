from typing import Optional, NamedTuple

import numpy as np

from common_image.ndimagedata import NdImageData


class HistResults(NamedTuple):
    sorted_most_freq_colors: np.ndarray
    sorted_most_freq_colors_counts: np.ndarray


def ndarray_to_hist(ndarray: np.ndarray, k: Optional[int] = None, normed: bool = True) -> HistResults:
    color_points = ndarray.reshape((-1, 1))
    unique_colors, unique_counts = np.unique(color_points, return_counts=True, axis=0)
    k = min(k, len(unique_counts)) if k is not None else len(unique_counts)
    most_freq_colors_indices = np.argpartition(unique_counts, len(unique_counts) - k - 1)[-k:]
    sorted_most_freq_colors_indices = most_freq_colors_indices[np.argsort(unique_counts[most_freq_colors_indices])]
    sorted_most_freq_colors_indices = sorted_most_freq_colors_indices[::-1]
    sorted_most_freq_colors = unique_colors[sorted_most_freq_colors_indices]
    sorted_most_freq_colors_counts = unique_counts[sorted_most_freq_colors_indices]
    if normed:
        return HistResults(sorted_most_freq_colors, sorted_most_freq_colors_counts / np.sum(
            sorted_most_freq_colors_counts))
    else:
        return HistResults(sorted_most_freq_colors, sorted_most_freq_colors_counts)


def ndimg_to_hist(ndimg: NdImageData, k: Optional[int] = None, normed: bool = True) -> HistResults:
    foreground_color_points = ndimg.ndimg[ndimg.bool_mask_ndimg]
    return ndarray_to_hist(foreground_color_points, k, normed)
