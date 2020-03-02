from math import ceil
from typing import Tuple, Iterable

import matplotlib.pyplot as plt
import numpy as np

from common.itertools_utils import do_by_batches


def plot_named_ndarrays_tuples(named_ndarray_tuples: Iterable[Tuple[Tuple[str, np.ndarray], ...]],
                               ncols: int, **imshow_kwargs) -> None:
    image_tuples = [tuple(named_ndarray[1] for named_ndarray in named_ndarray_tuple) for named_ndarray_tuple in named_ndarray_tuples]
    plot_image_tuples(image_tuples, ncols, **imshow_kwargs)


def plot_named_ndarrays_tuples_by_batches(named_ndarray_tuples: Iterable[Tuple[Tuple[str, np.ndarray], ...]],
                                          ncols: int, tuples_per_plot: int, **imshow_kwargs) -> None:
    do_by_batches(named_ndarray_tuples, tuples_per_plot, lambda batch: plot_named_ndarrays_tuples(batch, ncols, **imshow_kwargs))
    # image_tuples = [tuple(named_ndarray[1] for named_ndarray in named_ndarray_tuple) for named_ndarray_tuple in named_ndarray_tuples]
    # plot_image_tuples_by_batches(image_tuples, ncols, tuples_per_plot, **imshow_kwargs)


def plot_image_tuples(image_tuples: Iterable[Tuple[np.ndarray, ...]], ncols: int, **imshow_kwargs) -> None:
    images = [image for image_tuple in image_tuples for image in image_tuple]
    # image_tuples = list(image_tuples)
    # image_tuples = list(image_tuples)
    nrows = ceil(len(images) / ncols)
    i = 0
    # for image_tuple in image_tuples:
    for image in images:
        ax = plt.subplot(nrows, ncols, i + 1)
        # ax.set_title(str)
        ax.axis('off')
        image = image.squeeze()
        plt.imshow(image, **imshow_kwargs)
        i += 1
    plt.show()


def plot_image_tuples_by_batches(image_tuples: Iterable[Tuple[np.ndarray, ...]],
                                 ncols: int, tuples_per_plot: int, **imshow_kwargs) -> None:
    do_by_batches(image_tuples, tuples_per_plot, lambda batch: plot_image_tuples(batch, ncols, **imshow_kwargs))


def plot_labels_histogram(labels: np.ndarray) -> None:
    values, counts = np.unique(labels, return_counts=True)
    _ = plt.bar(values, counts, tick_label=values)
    plt.show()
