from pathlib import PurePath
from typing import Iterable, Tuple, TypeVar

import numpy as np
import openslide
from dataclasses import replace, asdict

from slice.annotation_shapely_utils import load_annotation_geoms
from common.itertools_utils import groupbyformat, map_inside_group
from slice.model.patch_geometry import PatchGeometryIterable
from slice.factory import create_annotations_patch_image_generator, create_patch_geometry_hooks_generator
from slice.model.patch_image import PatchImageIterable
from ndarray_persist.ndarray_persist_utils import save_named_ndarrays_to_hdf5, NamedNdarray, load_named_ndarrays_from_hdf5
from slice.model.patch_response import PatchResponse, PatchResponseIterable
from slice.model.patch_image_source_config import PatchImageSourceConfig
from slice.model.patch_image_config import PatchImageConfig


def process_pisc(cfg: PatchImageSourceConfig) -> PatchResponseIterable:
    cfg = fix_cfg(cfg)
    annotations_path = cfg.annotations_path
    annotation_geoms = load_annotation_geoms(annotations_path) if annotations_path else []
    pggf = create_patch_geometry_hooks_generator(annotation_geoms)
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


def process_pic(pgg: PatchGeometryIterable, cfg: PatchImageConfig) -> PatchImageIterable:
    cfg = fix_cfg(cfg)
    annotations_path = cfg.annotations_path
    annotation_geoms = load_annotation_geoms(annotations_path) if annotations_path else []
    pigf = create_annotations_patch_image_generator(annotation_geoms)
    # TODO wrap pig to adjust offset if not None
    pig = pigf.create(cfg.slide_path, cfg.level, pgg)
    return pig


def collect_responses_images_to_ndarray(patch_responses: PatchResponseIterable) -> np.ndarray:
    imgs = [pr.img.ndimg for pr in patch_responses]
    ndarray = np.stack(imgs)
    return ndarray

def collect_images_inside_groups(groups: Iterable[Tuple[str, PatchResponseIterable]]) -> Iterable[Tuple[str, np.ndarray]]:
    return map_inside_group(groups, collect_responses_images_to_ndarray)


def collect_responses_to_image_groups(patch_responses: PatchResponseIterable, group_key_format: str) -> Iterable[NamedNdarray]:
    response_groups = groupbyformat(patch_responses, group_key_format)
    image_groups = collect_images_inside_groups(response_groups)
    # image_groups = list(image_groups)
    return image_groups


if __name__ == '__main__':
    # TODO consider image and mask slide shifts
    # TODO consider (level, grid_length, stride) collection?
    # TODO consider imbalanced data
    # TODO consider different objective-powers of slides? Do rescale to some target objective-power?
    # TODO consider color mode conversion hooks (at least at start we dont need RGBA)
    # arrs1 = np.load(r"D:\slide_cbir_47\temp\npz_test.npz")
    # print(arrs1.files)
    # arrs = {
    #     'a': np.arange(5),
    #     'a/b': np.arange(10)
    # }
    # path=pathlib.Path(r"D:\slide_cbir_47\temp\C:\npz_test.npz")
    # print(path)
    # path.parent.mkdir(parents=True, exist_ok=True)
    # np.savez_compressed(path, **arrs)
    slide_path = r"D:\slide_cbir_47\temp\slides\slide-2019-09-19T18-08-52-R28-S3.mrxs"
    # annotations_path = r"D:\slide_cbir_47\temp\slides\slide-2019-09-19T18-08-52-R28-S3_annotations5.json"
    annotations_path = r"D:\slide_cbir_47\temp\slides\slide-2019-09-19T18-08-52-R28-S3_annotations8.json"

    h5py_file_path = r"D:\slide_cbir_47\temp\data.hdf5"
    zip_file_path = r"D:\slide_cbir_47\temp\data_zip.npz"
    folder_path = r"D:\slide_cbir_47\temp"

    named_ndarrays = load_named_ndarrays_from_hdf5(h5py_file_path)
    named_ndarrays = list(named_ndarrays)

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
    # pig = islice(pig, 10)
    pig = list(pig)
    format_str = r"{cfg.slide_path}/{cfg.level}/{cfg.grid_length}/{cfg.metadata[name]}/({pos[0]},{pos[1]})_{cfg.level}_{cfg.metadata[name]}"
    named_ndarrays = collect_responses_to_image_groups(pig, format_str)
    # format_str = r"{cfg.slide_path}/{cfg.level}/{cfg.grid_length}/{cfg.metadata[name]}/{cfg.level}"
    save_named_ndarrays_to_hdf5(named_ndarrays, h5py_file_path, "w")
    # save_ndarray_groups_to_zip(pig, format_str, zip_file_path)
    # save_ndarray_groups_to_folder(pig, format_str, folder_path, delete_working_folder=True)
    # collect_responses_hdf5(pig, format_str, h5py_file_path)

    # for p in pig:
    #     print(p[0])


def posix_path(s: str) -> str:
    pp = PurePath(s)
    return pp.as_posix()


CFG = TypeVar('CFG', PatchImageConfig, PatchImageSourceConfig)


def fix_cfg(cfg: CFG) -> CFG:
    if cfg.slide_path:
        cfg = replace(cfg, slide_path=posix_path(cfg.slide_path))
    if cfg.annotations_path:
        cfg = replace(cfg, annotations_path=posix_path(cfg.annotations_path))
    return cfg