import pathlib
from typing import Callable, Optional, List

from ndarray_persist.common import HDF5_EXTENSIONS, ARCHIVE_EXTENSIONS
from ndarray_persist.load.folder_ndarray_loader import load_names_from_folder
from ndarray_persist.load.hdf5_ndarray_loader import load_names_from_hdf5
from ndarray_persist.load.zip_ndarray_loader import load_names_from_zip

#
# def load_names(path: str,
#                name_filter: Callable[[str], bool] = lambda _: True,
#                name_pattern: Optional[str] = None) \
#         -> List[str]:
#     path = pathlib.Path(path)
#     if path.suffix in HDF5_EXTENSIONS:
#         return load_names_from_hdf5(path, name_filter, name_pattern)
#     elif path.suffix in ARCHIVE_EXTENSIONS:
#         return load_names_from_zip(path, name_filter, name_pattern)
#     elif path.is_dir():
#         return load_names_from_folder(path, name_filter, name_pattern)
#     else:
#         raise ValueError(f"Cant load from {path}")

# def load_named_ndarrays(path: str,
#                         name_filter: Callable[[str], bool] = lambda _: True,
#                         name_pattern: Optional[str] = None) \
#         -> Iterable[NamedNdarray]:
#     path = pathlib.Path(path)
#     if path.suffix in HDF5_EXTENSIONS:
#         return load_named_ndarrays_from_hdf5(path, name_filter, name_pattern)
#     elif path.suffix in ARCHIVE_EXTENSIONS:
#         return load_named_ndarrays_from_zip(path, name_filter, name_pattern)
#     elif path.is_dir():
#         return load_named_ndarrays_from_folder(path, name_filter, name_pattern)
#     else:
#         raise ValueError(f"Cant load from {path}")


