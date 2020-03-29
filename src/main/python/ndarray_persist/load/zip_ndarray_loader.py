import pathlib
from typing import Iterable, Callable, Optional, List
from zipfile import ZipFile

import imageio
import numpy as np

from ndarray_persist.common import _filter_name, NPY_EXTENSIONS
from ndarray_persist.load.ndarray_loader import NdarrayLoader


class ZipNdarrayLoader(NdarrayLoader):
    def __init__(self, file_path: str, names: Iterable[str],
                 ndarray_converter: Callable[[np.ndarray], np.ndarray] = None):
        super().__init__(ndarray_converter)
        self.file_path = file_path
        self.names = names

    @staticmethod
    def from_names(file_path: str, names: Iterable[str],
                   ndarray_converter: Callable[[np.ndarray], np.ndarray] = None):
        return ZipNdarrayLoader(file_path, names, ndarray_converter)

    @staticmethod
    def from_name_filter(file_path: str,
                         name_filter: Callable[[str], bool] = lambda _: True,
                         name_pattern: Optional[str] = None,
                         ndarray_converter: Callable[[np.ndarray], np.ndarray] = None):
        names = load_names_from_zip(file_path, name_filter, name_pattern)
        return ZipNdarrayLoader(file_path, names, ndarray_converter)

    def load_names(self) -> Iterable[str]:
        return self.names

    def load_ndarrays(self) -> Iterable[np.ndarray]:
        return load_ndarrays_from_zip(self.file_path, self.names, self.ndarray_converter)


def load_names_from_zip(file_path: str,
                        name_filter: Callable[[str], bool] = lambda _: True,
                        name_pattern: Optional[str] = None) -> List[str]:
    with ZipFile(file_path) as zip_root:
        names = [i.filename for i in zip_root.infolist() if not i.is_dir()]
    filtered_names = [name for name in names if _filter_name(name, name_filter, name_pattern)]
    filtered_names.sort()
    return filtered_names


def load_ndarrays_from_zip(file_path: str,
                           names: Iterable[str],
                           ndarray_converter: Callable[[np.ndarray], np.ndarray] = None) -> Iterable[np.ndarray]:
    with ZipFile(file_path) as zip_root:
        for name in names:
            with zip_root.open(name) as f:
                name = pathlib.Path(name)
                f = f.read()
                if name.suffix in NPY_EXTENSIONS:
                    ndarray = np.load(f)
                else:
                    ndarray = imageio.imread(f)
            if ndarray_converter:
                ndarray = ndarray_converter(ndarray)
            yield ndarray
