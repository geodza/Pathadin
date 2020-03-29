import pathlib
import re
from typing import Iterable, Callable, Optional, Tuple

import numpy as np
from skimage import io

from common.itertools_utils import peek
from common_image.core.resize import resize_ndarray

NamedNdarray = Tuple[str, np.ndarray]
HDF5_EXTENSIONS = ('.h5', '.hdf5')
NPY_EXTENSIONS = ('.npy')
NPZ_EXTENSIONS = ('.npz')
ZIP_EXTENSIONS = ('.zip')
DEFAULT_IMAGE_EXTENSION = '.png'
PNG_EXTENSIONS = ('.png')
JPEG_EXTENSIONS = ('.jpeg', '.jpg')


def stack_ndarrays(ndarrays: Iterable[np.ndarray],
                   count: int,
                   ndarray_converter: Callable[[np.ndarray], np.ndarray] = None) \
        -> np.ndarray:
    first, ndarrays = peek(ndarrays)
    first = ndarray_converter(first) if ndarray_converter else first
    shape = (count, *first.shape)
    ndarray = np.empty(shape, first.dtype)
    for i, arr in enumerate(ndarrays):
        arr = ndarray_converter(arr) if ndarray_converter else arr
        if arr.shape != first.shape:
            arr = resize_ndarray(arr, first.shape[:2]).reshape(first.shape)
        ndarray[i, ...] = arr
    return ndarray


def load_ndarray_from_filesystem(path: str) -> np.ndarray:
    path = pathlib.Path(path)
    if path.suffix in NPY_EXTENSIONS:
        return np.load(str(path))
    else:
        return io.imread(str(path))


def _filter_name(name: str, name_filter: Callable[[str], bool], name_pattern: Optional[str] = None) -> bool:
    return name_filter(name) and (not name_pattern or re.search(name_pattern, name))


def _build_valid_path(path: str) -> str:
    path_ = pathlib.PurePath(path)
    # TODO replace invalid chars
    return path_.relative_to(path_.anchor).as_posix()
