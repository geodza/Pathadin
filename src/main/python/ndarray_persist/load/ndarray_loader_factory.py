import pathlib
from typing import Callable, Optional, List

import numpy as np

from ndarray_persist.common import HDF5_EXTENSIONS, ARCHIVE_EXTENSIONS
from ndarray_persist.load.folder_ndarray_loader import FolderNdarrayLoader
from ndarray_persist.load.hdf5_ndarray_loader import HDF5NdarrayLoader
from ndarray_persist.load.ndarray_loader import NdarrayLoader
from ndarray_persist.load.zip_ndarray_loader import ZipNdarrayLoader


class NdarrayLoaderFactory:

    @staticmethod
    def from_names(path: str,
                   names: List[str],
                   ndarray_converter: Callable[[np.ndarray], np.ndarray] = None) -> NdarrayLoader:
        path = pathlib.Path(path)
        if path.suffix in HDF5_EXTENSIONS:
            return HDF5NdarrayLoader.from_names(path, names, ndarray_converter)
        elif path.suffix in ARCHIVE_EXTENSIONS:
            return ZipNdarrayLoader.from_names(path, names, ndarray_converter)
        elif path.is_dir():
            return FolderNdarrayLoader.from_names(path, names, ndarray_converter)
        else:
            raise ValueError(f"Cant load from {path}")

    @staticmethod
    def from_name_filter(path: str,
                         name_filter: Callable[[str], bool] = lambda _: True,
                         name_pattern: Optional[str] = None,
                         ndarray_converter: Callable[[np.ndarray], np.ndarray] = None) -> NdarrayLoader:
        path = pathlib.Path(path)
        if path.suffix in HDF5_EXTENSIONS:
            return HDF5NdarrayLoader.from_name_filter(path, name_filter, name_pattern, ndarray_converter)
        elif path.suffix in ARCHIVE_EXTENSIONS:
            return ZipNdarrayLoader.from_name_filter(path, name_filter, name_pattern, ndarray_converter)
        elif path.is_dir():
            return FolderNdarrayLoader.from_name_filter(path, name_filter, name_pattern, ndarray_converter)
        else:
            raise ValueError(f"Cant load from {path}")
