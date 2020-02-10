import json
import pathlib
import shutil
import warnings
from typing import Iterable, Tuple, List, NamedTuple

import h5py
import numpy as np
import openslide
from dataclasses import replace, asdict
from h5py import Dataset
from shapely.geometry import Polygon
from shapely.geometry.base import BaseGeometry
from skimage import io

from img.ndimagedata import NdImageData
from shapely_utils import annotation_to_geom
from slice.group_utils import groupbyformat, map_inside_group
from slice.patch_geometry_generator import PatchGeometryGenerator, create_patch_geometry_hooks_generator_factory, PatchPos
from slice.patch_image_generator import create_slide_annotations_patch_image_generator, PatchImageGenerator
from slice.slide_slice_config import PatchImageConfig, PatchImageSourceConfig, posix_path, fix_cfg
from slide_viewer.ui.odict.deep.model import AnnotationTreeItems


class PatchResponse(NamedTuple):
    pos: PatchPos
    polygon: Polygon
    img: NdImageData
    cfg: PatchImageConfig


PatchResponseGenerator = Iterable[PatchResponse]


def load_annotation_geoms(annotations_path: str) -> List[BaseGeometry]:
    annotations_container = AnnotationTreeItems.parse_file(annotations_path)
    annotations = annotations_container.annotations

    train_annotations = [a for a in annotations.values() if a.label != 'test']

    annotation_geoms = [annotation_to_geom(a, True) for a in train_annotations]
    return annotation_geoms


def update_dataset_image_attrs(dataset: Dataset):
    attrs = {"CLASS": np.string_('IMAGE'),
             "IMAGE_VERSION": np.string_("1.2"),
             "IMAGE_MINMAXRANGE": np.asarray([0, 255], dtype=np.uint8),
             "IMAGE_SUBCLASS": np.string_('IMAGE_TRUECOLOR'),
             "INTERLACE_MODE": np.string_('INTERLACE_PIXEL')}
    dataset.attrs.update(attrs)


def process_pisc(cfg: PatchImageSourceConfig) -> PatchResponseGenerator:
    cfg = fix_cfg(cfg)
    annotations_path = cfg.annotations_path
    annotation_geoms = load_annotation_geoms(annotations_path) if annotations_path else []
    pggf = create_patch_geometry_hooks_generator_factory(annotation_geoms)
    with openslide.OpenSlide(cfg.slide_path) as slide:
        source_size = slide.level_dimensions[0]
    pgg = pggf.create(source_size, cfg.grid_length, cfg.stride, cfg.offset_x, cfg.offset_y)
    # pgg = itertools.islice(pgg, 5)
    pig = process_pic(pgg, cfg)
    if not cfg.dependents:
        for (x, y), polygon, img in pig:
            yield PatchResponse((x, y), polygon, img, cfg)
    else:
        pgs = []
        for (x, y), polygon, img in pig:
            yield PatchResponse((x, y), polygon, img, cfg)
            pgs.append(((x, y), polygon))
        for dep in cfg.dependents:
            dep_ = replace(cfg, **asdict(dep))
            dep_ = fix_cfg(dep_)
            deppig = process_pic(pgs, dep_)
            for (x, y), polygon, img in deppig:
                yield PatchResponse((x, y), polygon, img, dep_)


def process_pic(pgg: PatchGeometryGenerator, cfg: PatchImageConfig) -> PatchImageGenerator:
    cfg = fix_cfg(cfg)
    annotations_path = cfg.annotations_path
    annotation_geoms = load_annotation_geoms(annotations_path) if annotations_path else []
    pigf = create_slide_annotations_patch_image_generator(annotation_geoms)
    # TODO wrap pig to adjust offset if not None
    pig = pigf.create(cfg.slide_path, cfg.level, pgg)
    return pig


def collect_responses_images_to_ndarray(prg: PatchResponseGenerator) -> np.ndarray:
    imgs = [pr.img.ndimg for pr in prg]
    ndarray = np.stack(imgs)
    return ndarray


def collect_images_inside_groups(groups: Iterable[Tuple[str, PatchResponseGenerator]]) -> Iterable[Tuple[str, np.ndarray]]:
    return map_inside_group(groups, collect_responses_images_to_ndarray)
    # for key, prg in groups:
    #     ndarray = collect_responses_images_to_ndarray(prg)
    #     yield (key, ndarray)
    # return itertools.starmap(lambda key, prg: (key, collect_responses_images_to_ndarray(prg)), groups)


def collect_responses_to_image_groups(prg: PatchResponseGenerator, group_key_format: str):
    dataset_path_format = posix_path(group_key_format)
    response_groups = groupbyformat(prg, dataset_path_format)
    # response_groups = list(response_groups)
    image_groups = collect_images_inside_groups(response_groups)
    image_groups = list(image_groups)
    return image_groups


def save_image_groups_to_hdf5(prg: PatchResponseGenerator, group_key_format: str,
                              file_path: str, file_mode: str = "a", compression="gzip", **dataset_kwargs):
    image_groups = collect_responses_to_image_groups(prg, group_key_format)
    file_path_path = pathlib.Path(file_path)
    file_path_path.parent.mkdir(parents=True, exist_ok=True)
    with h5py.File(file_path_path, file_mode) as f:
        for k, ndarray in image_groups:
            dataset_path = k
            if dataset_path in f:
                # TODO delete only if we cant update (different shape and dtype)
                del f[dataset_path]
            if ndarray.shape[0] == 1:
                dataset_data = ndarray.squeeze()
                dataset = f.create_dataset(dataset_path, data=dataset_data, compression=compression, **dataset_kwargs)
                update_dataset_image_attrs(dataset)
            else:
                dataset_data = ndarray
                dataset = f.create_dataset(dataset_path, data=dataset_data, compression=compression, **dataset_kwargs)
            dataset.attrs['cfg'] = json.dumps(asdict(cfg))
            # dataset.attrs['dataset_path_format'] = dataset_path_format


def save_image_groups_to_filesystem(prg: PatchResponseGenerator, group_key_format: str,
                                    root_folder: str, delete_working_folder=False):
    image_groups = collect_responses_to_image_groups(prg, group_key_format)
    predefined_working_folder = 'patches'
    working_folder = pathlib.Path(root_folder, predefined_working_folder)
    if delete_working_folder:
        shutil.rmtree(working_folder, True)
    working_folder.mkdir(parents=True, exist_ok=True)
    for k, ndarray in image_groups:
        if len(ndarray.shape) > 3 and ndarray.shape[0] != 1:
            # raise ValueError('Cant save multidim image')
            image = np.atleast_3d(ndarray.ravel())
            warnings.warn(f"ndarray with shape {ndarray.shape} reshaped to {image.shape}")
        else:
            image = ndarray.squeeze()
        image_path = pathlib.Path(k)
        if not image_path.suffix:
            image_path = image_path.with_suffix(".png")
        image_path = image_path.relative_to(image_path.anchor)
        image_path = working_folder.joinpath(image_path)
        image_path.parent.mkdir(parents=True, exist_ok=True)
        io.imsave(image_path, image)


if __name__ == '__main__':
    slide_path = r"D:\slide_cbir_47\temp\slides\slide-2019-09-19T18-08-52-R28-S3.mrxs"
    # annotations_path = r"D:\slide_cbir_47\temp\slides\slide-2019-09-19T18-08-52-R28-S3_annotations5.json"
    annotations_path = r"D:\slide_cbir_47\temp\slides\slide-2019-09-19T18-08-52-R28-S3_annotations8.json"
    h5py_file_path = r"D:\slide_cbir_47\temp\data.hdf5"
    level = 2
    grid_length = 256 * (level) ** 2
    stride = grid_length / 4
    cfg = PatchImageSourceConfig(slide_path, 2, annotations_path, metadata={"name": "label"},
                                 grid_length=grid_length, stride=stride, dependents=[
            # PatchImageConfig(slide_path, 0, metadata={"name": "image"}),
            # PatchImageConfig(slide_path, 1, metadata={"name": "image"}),
            PatchImageConfig(slide_path, 2, metadata={"name": "image"}),
        ])
    pig = process_pisc(cfg)
    format_str = r"{cfg.slide_path}/{cfg.level}/{cfg.grid_length}/{cfg.metadata[name]}/({pos[0]},{pos[1]})_{cfg.level}"
    # format_str = r"{cfg.slide_path}/{cfg.level}/{cfg.grid_length}/{cfg.metadata[name]}/{cfg.level}"
    save_image_groups_to_hdf5(pig, format_str, h5py_file_path, "w")
    # save_image_groups_to_filesystem(pig, format_str, r"D:\slide_cbir_47\temp", delete_working_folder=True)
    # collect_responses_hdf5(pig, format_str, h5py_file_path)
    # pig = islice(pig, 10)
    # for p in pig:
    #     print(p[0])
