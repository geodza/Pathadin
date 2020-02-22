import operator
import os
import pathlib
import re
import shutil
import warnings
from typing import Iterable, Tuple, Callable, Optional

import h5py
import numpy as np
from h5py import Dataset
from skimage import io

from ndarray_persist.h5py_utils import update_dataset_image_attrs

NamedNdarray = Tuple[str, np.ndarray]

HDF5_EXTENSIONS = ('.h5', '.hdf5')
ARCHIVE_EXTENSIONS = ('.npz', '.zip')
DEFAULT_IMAGE_EXTENSION = '.png'


def save_named_ndarrays(named_ndarrays: Iterable[NamedNdarray], path: str, delete_if_exists=False, verbosity=0) -> None:
    path = pathlib.Path(path)
    if path.is_dir():
        save_named_ndarrays_to_folder(named_ndarrays, path, delete_working_folder=delete_if_exists, verbosity=verbosity)
    elif not path.exists() and not path.suffix:
        save_named_ndarrays_to_folder(named_ndarrays, str(path), delete_working_folder=delete_if_exists, verbosity=verbosity)
    elif path.suffix in HDF5_EXTENSIONS:
        save_named_ndarrays_to_hdf5(named_ndarrays, str(path), 'w' if delete_if_exists else 'a', verbosity=verbosity)
    elif path.suffix in ARCHIVE_EXTENSIONS:
        if path.exists() and not delete_if_exists:
            raise ValueError('Appending to archive not supported, use delete_if_exists=True')
        else:
            save_named_ndarrays_to_zip(named_ndarrays, str(path), verbosity=verbosity)
    else:
        raise ValueError('Unsupported file extension')


def save_named_ndarrays_to_hdf5(named_ndarrays: Iterable[NamedNdarray],
                                file_path: str, file_mode: str = "a", compression="gzip", verbosity=0, **dataset_kwargs) -> None:
    file_path = pathlib.Path(file_path)
    file_path.parent.mkdir(parents=True, exist_ok=True)
    with h5py.File(file_path, file_mode) as f:
        for name, ndarray in named_ndarrays:
            ndarray_path = _build_valid_path(name)
            if verbosity > 0:
                print(f"saving {ndarray_path}")
            if ndarray_path in f:
                # TODO delete only if we cant update (different shape and dtype)
                del f[ndarray_path]
            ndarray = _squeeze_if_need(ndarray)
            if len(ndarray.shape) == 3:
                dataset = f.create_dataset(ndarray_path, data=ndarray, compression=compression, **dataset_kwargs)
                update_dataset_image_attrs(dataset)
            else:
                dataset = f.create_dataset(ndarray_path, data=ndarray, compression=compression, **dataset_kwargs)
            # dataset.attrs['cfg'] = json.dumps(asdict(cfg))
            # dataset.attrs['dataset_path_format'] = dataset_path_format


def save_named_ndarrays_to_zip(named_ndarrays: Iterable[NamedNdarray], file_path: str, verbosity=0) -> None:
    file_path = pathlib.Path(file_path)
    file_path.parent.mkdir(parents=True, exist_ok=True)
    ndarrays = {}
    for name, ndarray in named_ndarrays:
        ndarray_path = _build_valid_path(name)
        if verbosity > 0:
            print(f"saving {ndarray_path}")
        ndarray = _squeeze_if_need(ndarray)
        ndarrays[ndarray_path] = ndarray
    with open(file_path, 'wb') as f:
        # np.savez_compressed(str(file_path), **ndarrays)
        np.savez_compressed(f, **ndarrays)


def save_named_ndarrays_to_folder(named_ndarrays: Iterable[NamedNdarray], root_folder: str, delete_working_folder=False, verbosity=0) -> None:
    predefined_working_folder = 'patches'
    working_folder = pathlib.Path(root_folder, predefined_working_folder)
    if delete_working_folder:
        shutil.rmtree(working_folder, True)
    working_folder.mkdir(parents=True, exist_ok=True)
    for name, ndarray in named_ndarrays:
        ndarray_path = _build_valid_path(name)
        ndarray_path = working_folder.joinpath(ndarray_path)
        # ndarray_path = ndarray_path if ndarray_path.suffix else ndarray_path.with_suffix(DEFAULT_IMAGE_EXTENSION)
        if verbosity > 0:
            print(f"saving {ndarray_path}")
        ndarray = _squeeze_if_need(ndarray)
        save_ndarray_to_filesystem(ndarray, ndarray_path)


def save_ndarray_to_filesystem(ndarray: np.ndarray, path: str) -> None:
    path = pathlib.Path(path)
    # path = path if path.suffix else path.with_suffix('.npz')
    path.parent.mkdir(parents=True, exist_ok=True)
    if path.suffix == '.npy':
        np.save(str(path), ndarray)
    elif path.suffix in ARCHIVE_EXTENSIONS:
        np.savez_compressed(str(path), ndarray)
    else:
        save_ndarray_as_image_to_filesystem(ndarray, path)


def save_ndarray_as_image_to_filesystem(ndarray: np.ndarray, path: str) -> None:
    path = pathlib.Path(path)
    # path = path if path.suffix else path.with_suffix(DEFAULT_IMAGE_EXTENSION)
    path.parent.mkdir(parents=True, exist_ok=True)
    image = _squeeze_if_need(ndarray)
    if len(ndarray.shape) > 3 and ndarray.shape[0] != 1:
        # raise ValueError('Cant save multidim image')
        image = np.atleast_3d(ndarray.ravel())
        warnings.warn(f"ndarray with shape {ndarray.shape} reshaped to {image.shape}")
    if pathlib.Path(path).suffix:
        if pathlib.Path(path).suffix.lower() == '.png':
            io.imsave(path, image, check_contrast=False, compress_level=3)
        else:
            io.imsave(path, image, check_contrast=False)
    else:
        # we save in png format but do not add suffix to path because client
        # doesn't specify it and will expect the same name when loading it back to memory
        io.imsave(path, image, check_contrast=False, format='png', compress_level=3)


def load_named_ndarrays(path: str,
                        name_filter: Callable[[str], bool] = lambda _: True,
                        name_pattern: Optional[str] = None) \
        -> Iterable[NamedNdarray]:
    path = pathlib.Path(path)
    if path.suffix in HDF5_EXTENSIONS:
        return load_named_ndarrays_from_hdf5(path, name_filter, name_pattern)
    elif path.suffix in ARCHIVE_EXTENSIONS:
        return load_named_ndarrays_from_zip(path, name_filter, name_pattern)
    elif path.is_dir():
        return load_named_ndarrays_from_folder(path, name_filter, name_pattern)
    else:
        raise ValueError(f"Cant load from {path}")


def load_named_ndarrays_from_hdf5(file_path: str,
                                  name_filter: Callable[[str], bool] = lambda _: True,
                                  name_pattern: Optional[str] = None,
                                  force_copy_to_memory: bool = True) \
        -> Iterable[NamedNdarray]:
    filtered_names = []

    def visit(name, obj):
        if isinstance(obj, Dataset):
            if _filter_name(name, name_filter, name_pattern):
                filtered_names.append(name)

    filtered_names.sort()
    with h5py.File(file_path, 'r') as f:
        f.visititems(visit)
        for name in filtered_names:
            ndarray = f[name]
            ndarray = ndarray[:] if force_copy_to_memory else ndarray
            yield (name, ndarray)


def load_named_ndarrays_from_zip(file_path: str,
                                 name_filter: Callable[[str], bool] = lambda _: True,
                                 name_pattern: Optional[str] = None,
                                 mmap_mode=None) -> Iterable[NamedNdarray]:
    with np.load(file_path, mmap_mode=mmap_mode) as f:
        filtered_names = [name for name in f.keys() if _filter_name(name, name_filter, name_pattern)]
        filtered_names.sort()
        for name in filtered_names:
            ndarray = f[name]
            yield (name, ndarray)


def load_named_ndarrays_from_folder(root_folder: str,
                                    name_filter: Callable[[str], bool] = lambda _: True,
                                    name_pattern: Optional[str] = None) -> Iterable[NamedNdarray]:
    predefined_working_folder = 'patches'
    working_folder = pathlib.Path(root_folder, predefined_working_folder)
    filtered_names=[]
    for root, dirs, files in os.walk(working_folder, topdown=True):
        for name in files:
            # name = os.path.join(root, name)
            # name = str(pathlib.Path(root, name).with_suffix(""))
            name = str(pathlib.Path(root, name).relative_to(working_folder).as_posix())
            if _filter_name(name, name_filter, name_pattern):
                filtered_names.append(name)
    filtered_names.sort()
    for name in filtered_names:
        file_path = str(pathlib.Path(working_folder, name))
        ndarray = load_ndarray_from_filesystem(file_path)
        yield (name, ndarray)

def load_ndarray_from_filesystem(path: str) -> np.ndarray:
    path = pathlib.Path(path)
    if path.suffix in ('.npy', *ARCHIVE_EXTENSIONS):
        return np.load(str(path))
    else:
        return io.imread(str(path))


def named_ndarrays_to_ndarrays(named_ndarrays: Iterable[NamedNdarray]) -> Iterable[np.ndarray]:
    return map(operator.itemgetter(1), named_ndarrays)


def _filter_name(name: str, name_filter: Callable[[str], bool], name_pattern: Optional[str] = None) -> bool:
    return name_filter(name) and (not name_pattern or re.search(name_pattern, name))


def _build_valid_path(path: str) -> str:
    path_ = pathlib.PurePath(path)
    # TODO replace invalid chars
    return path_.relative_to(path_.anchor).as_posix()


def _squeeze_if_need(ndarray: np.ndarray) -> np.ndarray:
    if ndarray.shape[0] == 1:
        ndarray = ndarray.reshape(ndarray.shape[1:])
    return ndarray
