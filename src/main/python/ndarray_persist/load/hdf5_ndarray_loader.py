from typing import Iterable, Callable, Optional, List

import h5py
import numpy as np
from h5py import Dataset

from ndarray_persist.common import _filter_name
from ndarray_persist.load.ndarray_loader import NdarrayLoader


class HDF5NdarrayLoader(NdarrayLoader):
    def __init__(self, file_path: str, names: Iterable[str],
                 ndarray_converter: Callable[[np.ndarray], np.ndarray] = None, force_copy_to_memory: bool = True):
        super().__init__(ndarray_converter)
        self.file_path = file_path
        self.names = names
        self.force_copy_to_memory = force_copy_to_memory

    @staticmethod
    def from_names(file_path: str, names: Iterable[str],
                   ndarray_converter: Callable[[np.ndarray], np.ndarray] = None, force_copy_to_memory: bool = True):
        return HDF5NdarrayLoader(file_path, names, ndarray_converter, force_copy_to_memory)

    @staticmethod
    def from_name_filter(file_path: str,
                         name_filter: Callable[[str], bool] = lambda _: True,
                         name_pattern: Optional[str] = None,
                         ndarray_converter: Callable[[np.ndarray], np.ndarray] = None,
                         force_copy_to_memory: bool = True):
        names = load_names_from_hdf5(file_path, name_filter, name_pattern)
        return HDF5NdarrayLoader(file_path, names, ndarray_converter, force_copy_to_memory)

    def load_names(self) -> Iterable[str]:
        return self.names

    def load_ndarrays(self) -> Iterable[np.ndarray]:
        return load_ndarrays_from_hdf5(self.file_path, self.names, self.ndarray_converter, self.force_copy_to_memory)


def load_names_from_hdf5(file_path: str,
                         name_filter: Callable[[str], bool] = lambda _: True,
                         name_pattern: Optional[str] = None) -> List[str]:
    filtered_names = []

    def visit(name, obj):
        if isinstance(obj, Dataset):
            if _filter_name(name, name_filter, name_pattern):
                filtered_names.append(name)

    with h5py.File(file_path, 'r') as f:
        f.visititems(visit)
    filtered_names.sort()
    return filtered_names


def load_ndarrays_from_hdf5(file_path: str,
                            names: Iterable[str],
                            ndarray_converter: Callable[[np.ndarray], np.ndarray] = None,
                            force_copy_to_memory: bool = True
                            ) -> Iterable[np.ndarray]:
    with h5py.File(file_path, 'r') as f:
        for name in names:
            ndarray = f[name]
            ndarray = ndarray[:] if force_copy_to_memory else ndarray
            if ndarray_converter:
                ndarray = ndarray_converter(ndarray)
            yield ndarray
