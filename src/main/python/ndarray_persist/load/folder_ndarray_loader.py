import os
import pathlib
from typing import Iterable, Callable, List, Optional

import numpy as np

from ndarray_persist.common import _filter_name, load_ndarray_from_filesystem
from ndarray_persist.load.ndarray_loader import NdarrayLoader


class FolderNdarrayLoader(NdarrayLoader):
    def __init__(self, root_folder: str, names: Iterable[str], ndarray_converter: Callable[[np.ndarray], np.ndarray] = None):
        super().__init__(ndarray_converter)
        self.root_folder = root_folder
        self.names = names

    @staticmethod
    def from_names(root_folder: str, names: Iterable[str],
                   ndarray_converter: Callable[[np.ndarray], np.ndarray] = None):
        return FolderNdarrayLoader(root_folder, names, ndarray_converter)

    @staticmethod
    def from_name_filter(root_folder: str,
                         name_filter: Callable[[str], bool] = lambda _: True,
                         name_pattern: Optional[str] = None,
                         ndarray_converter: Callable[[np.ndarray], np.ndarray] = None):
        names = load_names_from_folder(root_folder, name_filter, name_pattern)
        return FolderNdarrayLoader(root_folder, names, ndarray_converter)

    def load_names(self) -> Iterable[str]:
        return self.names

    def load_ndarrays(self) -> Iterable[np.ndarray]:
        return load_ndarrays_from_folder(self.root_folder, self.names, self.ndarray_converter)


def load_names_from_folder(root_folder: str,
                           name_filter: Callable[[str], bool] = lambda _: True,
                           name_pattern: Optional[str] = None) -> List[str]:
    predefined_working_folder = 'patches'
    working_folder = pathlib.Path(root_folder, predefined_working_folder)
    filtered_names = []
    for root, dirs, files in os.walk(working_folder, topdown=True):
        for name in files:
            # name = os.path.join(root, name)
            # name = str(pathlib.Path(root, name).with_suffix(""))
            name = str(pathlib.Path(root, name).relative_to(working_folder).as_posix())
            if _filter_name(name, name_filter, name_pattern):
                filtered_names.append(name)
    filtered_names.sort()
    return filtered_names


def load_ndarrays_from_folder(root_folder: str,
                              names: Iterable[str],
                              ndarray_converter: Callable[[np.ndarray], np.ndarray] = None
                              ) -> Iterable[np.ndarray]:
    predefined_working_folder = 'patches'
    working_folder = pathlib.Path(root_folder, predefined_working_folder)
    for name in names:
        file_path = str(pathlib.Path(working_folder, name))
        ndarray = load_ndarray_from_filesystem(file_path)
        if ndarray_converter:
            ndarray = ndarray_converter(ndarray)
        yield ndarray
