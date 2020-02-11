import pathlib
import shutil
import warnings
from typing import Iterable, Tuple

import h5py
import numpy as np
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
        if ndarray_path.suffix in ('.npz', '.npy'):
            save_ndarray_to_filesystem(ndarray, ndarray_path)
        else:
            save_ndarray_as_image_to_filesystem(ndarray, ndarray_path)


def save_ndarray_to_filesystem(ndarray: np.ndarray, path: str) -> None:
    path = pathlib.Path(path)
    path = path if path.suffix else path.with_suffix('.npz')
    path.parent.mkdir(parents=True, exist_ok=True)
    if path.suffix == '.npy':
        np.save(str(path), ndarray)
    elif path.suffix == '.npz':
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


def _build_valid_path(path: str):
    path_ = pathlib.PurePath(path)
    # TODO replace invalid chars
    return path_.relative_to(path_.anchor).as_posix()


def _squeeze_if_need(ndarray: np.ndarray):
    if ndarray.shape[0] == 1:
        ndarray = ndarray.reshape(ndarray.shape[1:])
    return ndarray
