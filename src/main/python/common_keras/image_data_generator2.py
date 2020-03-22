from typing import Iterable, Tuple

import numpy as np
from keras_preprocessing.image import ImageDataGenerator

from common.itertools_utils import batchify
from ndarray_persist.common import stack_ndarrays


def tuples_batch_to_batches_tuple(tuples_batch: Iterable[Tuple[np.ndarray, np.ndarray]]):
    x, y = zip(*tuples_batch)
    batches_tuple = (list(x), list(y))
    return batches_tuple


class ImageDataGenerator2(ImageDataGenerator):
    # TODO raise Error for unsupported methods.
    # shuffle works only inside batch and not globally! You should shuffle inputs yourself.

    def flow_from_samples_generator(self, samples: Iterable[Tuple[np.ndarray, np.ndarray]], batch_size: int):
        # X_Y_iterable = batchify(samples_generator, batch_size, tuples_batch_to_batches_tuple)
        tuples_batches = batchify(samples, batch_size, tuples_batch_to_batches_tuple)
        for tuples_batch in tuples_batches:
            X_Y = tuples_batch_to_batches_tuple(tuples_batch)
            X_Y_ = next(self.flow(X_Y, batch_size=batch_size, shuffle=True))
            yield X_Y_
            # yield self.flow(X_Y, batch_size=batch_size, shuffle=True)

    def flow_from_generators(self, images: Iterable[np.ndarray], labels: Iterable[np.ndarray], batch_size: int):
        image_batches = batchify(images, batch_size)
        label_batches = batchify(labels, batch_size)
        for image_batch, label_batch in zip(image_batches, label_batches):
            X = stack_ndarrays(image_batch, batch_size)
            Y = stack_ndarrays(label_batch, batch_size)
            X_Y_ = next(self.flow(X, Y, batch_size=batch_size, shuffle=True))
            yield X_Y_
