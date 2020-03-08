from typing import Iterable, Callable, Optional, List

import numpy as np

from ndarray_persist.common import _filter_name
from ndarray_persist.load.ndarray_loader import NdarrayLoader


class ZipNdarrayLoader(NdarrayLoader):
    def __init__(self, file_path: str, names: Iterable[str],
                 ndarray_converter: Callable[[np.ndarray], np.ndarray] = None, mmap_mode=None):
        super().__init__(ndarray_converter)
        self.file_path = file_path
        self.names = names
        self.mmap_mode = mmap_mode

    @staticmethod
    def from_names(file_path: str, names: Iterable[str],
                   ndarray_converter: Callable[[np.ndarray], np.ndarray] = None, mmap_mode=None):
        return ZipNdarrayLoader(file_path, names, ndarray_converter, mmap_mode)

    @staticmethod
    def from_name_filter(file_path: str,
                         name_filter: Callable[[str], bool] = lambda _: True,
                         name_pattern: Optional[str] = None,
                         ndarray_converter: Callable[[np.ndarray], np.ndarray] = None,
                         mmap_mode=None):
        names = load_names_from_zip(file_path, name_filter, name_pattern)
        return ZipNdarrayLoader(file_path, names, ndarray_converter, mmap_mode)

    def load_names(self) -> Iterable[str]:
        return self.names

    def load_ndarrays(self) -> Iterable[np.ndarray]:
        return load_ndarrays_from_zip(self.file_path, self.names, self.ndarray_converter, self.mmap_mode)


def load_names_from_zip(file_path: str,
                        name_filter: Callable[[str], bool] = lambda _: True,
                        name_pattern: Optional[str] = None) -> List[str]:
    with np.load(file_path) as f:
        filtered_names = [name for name in f.keys() if _filter_name(name, name_filter, name_pattern)]
    filtered_names.sort()
    return filtered_names


def load_ndarrays_from_zip(file_path: str,
                           names: Iterable[str],
                           ndarray_converter: Callable[[np.ndarray], np.ndarray] = None,
                           mmap_mode=None) -> Iterable[np.ndarray]:
    with np.load(file_path, mmap_mode=mmap_mode) as f:
        for name in names:
            ndarray = f[name]
            if ndarray_converter:
                ndarray = ndarray_converter(ndarray)
            yield ndarray
