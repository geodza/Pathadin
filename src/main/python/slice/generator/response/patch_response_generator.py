from dataclasses import replace, asdict
from shapely.affinity import translate

from slice.annotation_shapely_utils import load_annotation_geoms
from slice.factory import create_patch_geometry_hooks_generator, create_patch_pos_generator
from slice.generator.image.config_patch_image_generator import process_pic
from slice.model.patch_image_source_config import PatchImageSourceConfig, PatchImageSourceConfigIterable
from slice.model.patch_response import PatchResponseIterable, PatchResponse
from slice.patch_config_utils import fix_cfg


class PatchResponseGenerator():
    def create(self, patch_image_source_configs: PatchImageSourceConfigIterable) -> PatchResponseIterable:
        for cfg in patch_image_source_configs:
            for res in process_pisc(cfg):
                yield res


def process_pisc(cfg: PatchImageSourceConfig) -> PatchResponseIterable:
    # TODO consider image and mask slide shifts
    # TODO consider (level, grid_length, stride) collection?
    # TODO consider imbalanced data
    # TODO consider different objective-powers of slides? Do rescale to some target objective-power?
    # TODO consider color mode conversion hooks (at least at start we dont need RGBA)
    cfg = fix_cfg(cfg)
    stride_x = cfg.stride_x if cfg.stride_x else cfg.patch_size[0]
    stride_y = cfg.stride_y if cfg.stride_y else cfg.patch_size[1]
    patch_positions = create_patch_pos_generator(cfg.slide_path, stride_x, stride_y, cfg.offset_x, cfg.offset_y).create()
    annotation_geoms = load_annotation_geoms(cfg.annotations_path) if cfg.annotations_path else []
    patch_geometries = create_patch_geometry_hooks_generator(cfg.slide_path, cfg.patch_size, annotation_geoms).create(patch_positions)
    if cfg.offset_x and cfg.offset_y:
        patch_geometries = map(lambda p: translate(p, cfg.offset_x, cfg.offset_y), patch_geometries)
    # patch_geometries = itertools.islice(patch_geometries, 5)
    patch_images = process_pic(patch_geometries, cfg)
    if not cfg.dependents:
        for (x, y), polygon, img in patch_images:
            yield PatchResponse((x, y), polygon, img, cfg)
    else:
        patch_source_geometries = []
        for (x, y), polygon, img in patch_images:
            yield PatchResponse((x, y), polygon, img, cfg)
            patch_source_geometries.append(((x, y), polygon))
        for dep in cfg.dependents:
            dep_ = replace(cfg, **asdict(dep))
            dep_ = fix_cfg(dep_)
            deppig = process_pic(patch_source_geometries, dep_)
            for (x, y), polygon, img in deppig:
                yield PatchResponse((x, y), polygon, img, dep_)
