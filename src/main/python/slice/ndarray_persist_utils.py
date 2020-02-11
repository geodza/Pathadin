import os
import pathlib
import shutil
import warnings
from typing import Iterable, Tuple, Callable

import h5py
import numpy as np
from h5py import Dataset
from skimage import io

from slice.h5py_utils import update_dataset_image_attrs

NamedNdarray = Tuple[str, np.ndarray]


def save_named_ndarrays_to_hdf5(named_ndarrays: Iterable[NamedNdarray],
                                file_path: str, file_mode: str = "a", compression="gzip", **dataset_kwargs) -> None:
    file_path = pathlib.Path(file_path)
    file_path.parent.mkdir(parents=True, exist_ok=True)
    with h5py.File(file_path, file_mode) as f:
        for name, ndarray in named_ndarrays:
            ndarray_path = _build_valid_path(name)
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


def save_named_ndarrays_to_zip(named_ndarrays: Iterable[NamedNdarray], file_path: str) -> None:
    file_path = pathlib.Path(file_path)
    file_path.parent.mkdir(parents=True, exist_ok=True)
    ndarrays = {}
    for name, ndarray in named_ndarrays:
        ndarray_path = _build_valid_path(name)
        ndarray = _squeeze_if_need(ndarray)
        ndarrays[ndarray_path] = ndarray
    np.savez_compressed(str(file_path), **ndarrays)


def save_named_ndarrays_to_folder(named_ndarrays: Iterable[NamedNdarray], root_folder: str, delete_working_folder=False) -> None:
    predefined_working_folder = 'patches'
    working_folder = pathlib.Path(root_folder, predefined_working_folder)
    if delete_working_folder:
        shutil.rmtree(working_folder, True)
    working_folder.mkdir(parents=True, exist_ok=True)
    for name, ndarray in named_ndarrays:
        ndarray_path = _build_valid_path(name)
        ndarray_path = working_folder.joinpath(ndarray_path)
        ndarray_path = ndarray_path if ndarray_path.suffix else ndarray_path.with_suffix('.png')
        ndarray = _squeeze_if_need(ndarray)
        if ndarray_path.suffix in ('.npz', '.npy', '.zip'):
            save_ndarray_to_filesystem(ndarray, ndarray_path)
        else:
            save_ndarray_as_image_to_filesystem(ndarray, ndarray_path)


def save_ndarray_to_filesystem(ndarray: np.ndarray, path: str) -> None:
    path = pathlib.Path(path)
    path = path if path.suffix else path.with_suffix('.npz')
    path.parent.mkdir(parents=True, exist_ok=True)
    if path.suffix == '.npy':
        np.save(str(path), ndarray)
    elif path.suffix in ('.npz', '.zip'):
        np.savez_compressed(str(path), ndarray)


def save_ndarray_as_image_to_filesystem(ndarray: np.ndarray, path: str) -> None:
    path = pathlib.Path(path)
    path = path if path.suffix else path.with_suffix('.png')
    path.parent.mkdir(parents=True, exist_ok=True)
    image = _squeeze_if_need(ndarray)
    if len(ndarray.shape) > 3 and ndarray.shape[0] != 1:
        # raise ValueError('Cant save multidim image')
        image = np.atleast_3d(ndarray.ravel())
        warnings.warn(f"ndarray with shape {ndarray.shape} reshaped to {image.shape}")

    io.imsave(path, image, check_contrast=False)


def load_named_arrays_from_hdf5(file_path: str, name_filter: Callable[[str], bool] = lambda _: True, force_copy_to_memory=True) \
        -> Iterable[NamedNdarray]:
    filtered_names = []

    def visit(name, obj):
        if isinstance(obj, Dataset):
            if name_filter(name):
                filtered_names.append(name)

    with h5py.File(file_path, 'r') as f:
        f.visititems(visit)
        for name in filtered_names:
            ndarray = f[name]
            ndarray = ndarray[:] if force_copy_to_memory else ndarray
            yield (name, ndarray)


def load_named_arrays_from_zip(file_path: str, name_filter: Callable[[str], bool] = lambda _: True, mmap_mode=None) -> Iterable[NamedNdarray]:
    with np.load(file_path, mmap_mode=mmap_mode) as f:
        for name in f.keys():
            if name_filter(name):
                ndarray = f[name]
                yield (name, ndarray)


def load_named_arrays_from_folder(root_folder: str, name_filter: Callable[[str], bool] = lambda _: True) -> Iterable[NamedNdarray]:
    for root, dirs, files in os.walk(root_folder, topdown=True):
        for name in files:
            name = os.path.join(root, name)
            if name_filter(name):
                ndarray = load_ndarray_from_filesystem(name)
                yield (name, ndarray)


def load_ndarray_from_filesystem(path: str) -> np.ndarray:
    path = pathlib.Path(path)
    if path.suffix in ('.npy'):
        return np.load(str(path))
    else:
        return io.imread(str(path))


def _build_valid_path(path: str) -> str:
    path_ = pathlib.PurePath(path)
    # TODO replace invalid chars
    return path_.relative_to(path_.anchor).as_posix()


def _squeeze_if_need(ndarray: np.ndarray) -> np.ndarray:
    if ndarray.shape[0] == 1:
        ndarray = ndarray.reshape(ndarray.shape[1:])
    return ndarray
