import glob
import itertools
import os
import random
from typing import Iterable, Tuple

import numpy as np
from skimage import img_as_float, io, transform




def flow_ndimgs_from_directory(dir, shuffle=True) -> Iterable[Tuple[str, np.ndarray]]:
    image_pathes = glob.glob(os.path.join(dir, "*.png"))
    if shuffle:
        random.seed(0)
        random.shuffle(image_pathes)
    else:
        image_pathes.sort()
    for i, image_path in enumerate(image_pathes):
        ndimg = io.imread(image_path)
        # ndimg = transform.resize(ndimg, (256, 256))
        # ndimg = img_as_float(ndimg)
        yield image_path, ndimg


def flow_samples_from_directories(image_dir, label_dir, shuffle=True) -> Iterable[Tuple[np.ndarray, np.ndarray]]:
    for image_path, ndimg in flow_ndimgs_from_directory(image_dir, shuffle):
        image_name = os.path.basename(image_path)
        label_path = os.path.join(label_dir, image_name)
        label_ndimg = io.imread(label_path, as_gray=True)
        label_ndimg = transform.resize(label_ndimg, (256, 256))
        label_ndimg = img_as_float(label_ndimg)
        ndimg = np.atleast_3d(ndimg)
        label_ndimg = np.atleast_3d(label_ndimg)
        yield ndimg, label_ndimg


def flow_test_samples_from_directory(dir):
    for img_path, ndimg in flow_ndimgs_from_directory(dir, False):
        ndimg = np.atleast_3d(ndimg)
        yield ndimg


def batchify(generator, batch_size):
    items = []
    for i, item in enumerate(generator):
        items.append(item)
        if (i + 1) % batch_size == 0:
            yield items
            items = []
    if items:
        yield items


def star_batchify(generator, batch_size):
    items = []
    for i, item in enumerate(generator):
        items.extend(item)
        if (i + 1) % batch_size == 0:
            tuple_length = len(item)
            yield tuple(items[j:None:tuple_length] for j in range(tuple_length))
            items = []
    if items:
        tuple_length = len(items) // batch_size
        yield tuple(items[j:None:tuple_length] for j in range(tuple_length))


def tuple_map(func, tuple_generator):
    results = []
    for tuple_ in tuple_generator:
        for item in tuple_:
            res = func(item)
            results.append(res)
        yield tuple(results)
        results = []


def to_ndarray(source):
    return np.array(source)


if __name__ == '__main__':
    grid_length = 256
    images = list(flow_ndimgs_from_directory(f'{grid_length}/train/image', False))
    print(images)

    # for batch in tuple_map(to_ndarray, star_batchify(flow_samples_from_directories(f'{grid_length}/train/image', f'{grid_length}/train/label'), 4)):
    #     print(len(batch))
    #
    # data_gen_args = dict(rotation_range=0.2,
    #                      width_shift_range=0.05,
    #                      height_shift_range=0.05,
    #                      shear_range=0.05,
    #                      zoom_range=0.05,
    #                      horizontal_flip=True,
    #                      fill_mode='nearest')
    # myGene = trainGenerator(1, f'{grid_length}/train', 'image', 'label', data_gen_args)
    # for t in islice(myGene, 1):
    #     print(t)

    # for ts in flow_test_samples_from_directory(f'{grid_length}/test/image'):
    #     print(ts)
    # for ts in batchify(flow_test_samples_from_directory(f'{grid_length}/test/image'), 4):
    #     print(ts)
    # for ts in map(to_ndarray, batchify(flow_test_samples_from_directory(f'{grid_length}/train/image'), 4)):
    #     print(ts)
    samples_gen = flow_samples_from_directories(f'{grid_length}/train/image', f'{grid_length}/train/label', False)
    samples_gen_list = list(samples_gen)

    for ts in map(to_ndarray, batchify(flow_test_samples_from_directory(f'{grid_length}/train/image'), 1)):
        print(ts)

    myGene = itertools.cycle(tuple_map(to_ndarray,
                                       star_batchify(
                                           flow_samples_from_directories(f'{grid_length}/train/image', f'{grid_length}/train/label'), 2)))
    for b in itertools.islice(myGene, 3):
        print(b)
