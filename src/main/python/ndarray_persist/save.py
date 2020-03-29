import pathlib
import shutil
import warnings
from typing import Iterable, BinaryIO
from zipfile import ZipFile

import h5py
import imageio
import numpy as np
from skimage import io

from ndarray_persist.common import _build_valid_path, NamedNdarray, HDF5_EXTENSIONS, ZIP_EXTENSIONS, NPZ_EXTENSIONS, PNG_EXTENSIONS, JPEG_EXTENSIONS, \
    DEFAULT_IMAGE_EXTENSION
from ndarray_persist.h5py_utils import update_dataset_image_attrs


def save_named_ndarrays(named_ndarrays: Iterable[NamedNdarray], path: str, delete_if_exists=False, verbosity=0) -> None:
    path = pathlib.Path(path)
    if path.is_dir():
        save_named_ndarrays_to_folder(named_ndarrays, path, delete_working_folder=delete_if_exists, verbosity=verbosity)
    elif not path.exists() and not path.suffix:
        save_named_ndarrays_to_folder(named_ndarrays, str(path), delete_working_folder=delete_if_exists, verbosity=verbosity)
    elif path.suffix in HDF5_EXTENSIONS:
        save_named_ndarrays_to_hdf5(named_ndarrays, str(path), 'w' if delete_if_exists else 'a', verbosity=verbosity)
    elif path.suffix in NPZ_EXTENSIONS:
        if path.exists() and not delete_if_exists:
            raise ValueError('Appending to archive not supported, use delete_if_exists=True')
        else:
            save_named_ndarrays_to_npz(named_ndarrays, str(path), verbosity=verbosity)
    elif path.suffix in ZIP_EXTENSIONS:
        if path.exists() and not delete_if_exists:
            raise ValueError('Appending to archive not supported, use delete_if_exists=True')
        else:
            save_named_ndarrays_to_zip(named_ndarrays, str(path), verbosity=verbosity)
    else:
        raise ValueError('Unsupported file extension')
    if verbosity > 0:
        print(f"successfully saved to: {path}")


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
        # ndarray = _squeeze_if_need(ndarray)
        save_ndarray_to_filesystem(ndarray, ndarray_path)


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
            # ndarray = _squeeze_if_need(ndarray)
            if len(ndarray.shape) == 3 or len(ndarray.shape) == 2:
                dataset = f.create_dataset(ndarray_path, data=ndarray, compression=compression, **dataset_kwargs)
                update_dataset_image_attrs(dataset)
            else:
                dataset = f.create_dataset(ndarray_path, data=ndarray, compression=compression, **dataset_kwargs)
            # dataset.attrs['cfg'] = json.dumps(asdict(cfg))
            # dataset.attrs['dataset_path_format'] = dataset_path_format


def save_named_ndarrays_to_npz(named_ndarrays: Iterable[NamedNdarray], file_path: str, verbosity=0) -> None:
    file_path = pathlib.Path(file_path)
    file_path.parent.mkdir(parents=True, exist_ok=True)
    ndarrays = {}
    for name, ndarray in named_ndarrays:
        ndarray_path = _build_valid_path(name)
        if verbosity > 0:
            print(f"saving {ndarray_path}")
        # ndarray = _squeeze_if_need(ndarray)
        ndarrays[ndarray_path] = ndarray
    with open(file_path, 'wb') as f:
        # np.savez_compressed(str(file_path), **ndarrays)
        np.savez_compressed(f, **ndarrays)


def save_named_ndarrays_to_zip(named_ndarrays: Iterable[NamedNdarray], file_path: str, verbosity=0) -> None:
    file_path = pathlib.Path(file_path)
    file_path.parent.mkdir(parents=True, exist_ok=True)
    with ZipFile(file_path, 'w') as zip_root:
        for name, ndarray in named_ndarrays:
            ndarray_path = _build_valid_path(name)
            if verbosity > 0:
                print(f"saving {ndarray_path}")
            ndarray_path = pathlib.Path(ndarray_path)
            with zip_root.open(str(ndarray_path), 'w') as f:
                if ndarray_path.suffix == '.npy':
                    np.save(f, ndarray)
                elif ndarray_path.suffix in NPZ_EXTENSIONS:
                    np.savez_compressed(str(ndarray_path), ndarray)
                else:
                    format = ndarray_path.suffix
                    save_ndarray_as_image_to_fileobj(ndarray, f, format)


def save_ndarray_to_filesystem(ndarray: np.ndarray, path: str) -> None:
    path = pathlib.Path(path)
    # path = path if path.suffix else path.with_suffix('.npz')
    path.parent.mkdir(parents=True, exist_ok=True)
    if path.suffix == '.npy':
        np.save(str(path), ndarray)
    elif path.suffix in ZIP_EXTENSIONS:
        np.savez_compressed(str(path), ndarray)
    else:
        save_ndarray_as_image_to_filesystem(ndarray, path)


def save_ndarray_as_image_to_filesystem(ndarray: np.ndarray, path: str) -> None:
    path = pathlib.Path(path)
    # path = path if path.suffix else path.with_suffix(DEFAULT_IMAGE_EXTENSION)
    path.parent.mkdir(parents=True, exist_ok=True)
    image = ndarray
    # image = _squeeze_if_need(ndarray)
    if len(ndarray.shape) > 3 and ndarray.shape[0] != 1:
        # raise ValueError('Cant save multidim image')
        image = np.atleast_3d(ndarray.ravel())
        warnings.warn(f"ndarray with shape {ndarray.shape} reshaped to {image.shape}")
    #
    if pathlib.Path(path).suffix:
        if pathlib.Path(path).suffix.lower() == '.png':
            io.imsave(path, image, check_contrast=False, compress_level=3)
        else:
            io.imsave(path, image, check_contrast=False)
    else:
        # we save in png format but do not add suffix to path because client
        # doesn't specify it and will expect the same name when loading it back to memory
        io.imsave(path, image, check_contrast=False, format='png', compress_level=3)


def save_ndarray_as_image_to_fileobj(ndarray: np.ndarray, fileobj: BinaryIO, format: str, **kwargs) -> None:
    image = ndarray
    if len(ndarray.shape) > 3 and ndarray.shape[0] != 1:
        # raise ValueError('Cant save multidim image')
        image = np.atleast_3d(ndarray.ravel())
        warnings.warn(f"ndarray with shape {ndarray.shape} reshaped to {image.shape}")
    kwargs = dict(kwargs) if kwargs else {}
    format = format if format else DEFAULT_IMAGE_EXTENSION
    if format in PNG_EXTENSIONS and 'compress_level' not in kwargs:
        kwargs['compress_level'] = 3
    if format in JPEG_EXTENSIONS and 'quality' not in kwargs:
        kwargs['quality'] = 75
    imageio.imwrite(fileobj, image, format=format, **kwargs)
