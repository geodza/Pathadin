from dataclasses import dataclass

from slice.annotation_shapely_utils import load_annotation_geoms, create_zlayers_rtrees
from slice.generator.image.annotations_patch_image_generator import AnnotationsPatchImageGenerator
from slice.generator.image.patch_image_generator import PatchImageGenerator
from slice.model.patch_geometry import PatchGeometryIterable
from slice.model.patch_image import PatchImageIterable
from slice.model.patch_image_config import PatchImageConfig
from slice.patch_config_utils import fix_cfg


@dataclass
class ConfigPatchImageGenerator(PatchImageGenerator):
    cfg: PatchImageConfig

    def create(self, patch_geometries: PatchGeometryIterable) -> PatchImageIterable:
        return process_pic(patch_geometries, self.cfg)


def process_pic(patch_geometries: PatchGeometryIterable, cfg: PatchImageConfig) -> PatchImageIterable:
    cfg = fix_cfg(cfg)
    annotations_path = cfg.annotations_path
    annotation_geoms = load_annotation_geoms(annotations_path) if annotations_path else []
    zlayers_rtrees = create_zlayers_rtrees(annotation_geoms)
    # TODO wrap pig to adjust offset if not None
    patch_images = AnnotationsPatchImageGenerator(cfg.slide_path, cfg.level, cfg.rescale_result_image, zlayers_rtrees).create(patch_geometries)
    return patch_images
