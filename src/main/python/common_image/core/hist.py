from typing import Optional, NamedTuple

import numpy as np

from common.numpy_utils import optimized_unique
from common.timeit_utils import timing
from common_image.model.ndimg import Ndimg


class HistResults(NamedTuple):
	sorted_most_freq_colors: np.ndarray
	sorted_most_freq_colors_counts: np.ndarray


@timing
def ndarray_to_hist(ndarray: np.ndarray, k: Optional[int] = None, normed: bool = True) -> HistResults:
	unique_colors, unique_counts = timing(optimized_unique)(ndarray)
	k = min(k, len(unique_counts)) if k is not None else len(unique_counts)
	most_freq_colors_indices = timing(np.argpartition)(unique_counts, len(unique_counts) - k - 1)[-k:]
	sorted_most_freq_colors_indices = most_freq_colors_indices[
		timing(np.argsort)(unique_counts[most_freq_colors_indices])]
	sorted_most_freq_colors_indices = sorted_most_freq_colors_indices[::-1]
	sorted_most_freq_colors = unique_colors[sorted_most_freq_colors_indices]
	sorted_most_freq_colors_counts = unique_counts[sorted_most_freq_colors_indices]
	if normed:
		return HistResults(sorted_most_freq_colors, sorted_most_freq_colors_counts / np.sum(
			sorted_most_freq_colors_counts))
	else:
		return HistResults(sorted_most_freq_colors, sorted_most_freq_colors_counts)


@timing
def ndimg_to_hist(ndimg: Ndimg, k: Optional[int] = None, normed: bool = True) -> HistResults:
	ndarray = ndimg.ndarray[ndimg.bool_mask_ndarray] if ndimg.bool_mask_ndarray is not None else ndimg.ndarray
	return ndarray_to_hist(ndarray, k, normed)


if __name__ == '__main__':
	a = np.array([1, 2, 3, 4], dtype=np.uint8)
	print(a)
	b = a.view(dtype=np.uint32)
	print(b)
	a = np.random.randint(255, size=(int(1e6), 4), dtype=np.uint8)
	b = timing(np.unique)(a, axis=0)
	b = timing(np.unique)(a)
	av = a.view(dtype=np.uint32)
	print('av', av.shape, av.dtype)
	b = timing(np.unique)(av, axis=0)
	b = timing(np.unique)(av)
	print(a)
