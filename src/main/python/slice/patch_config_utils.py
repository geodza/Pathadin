from pathlib import PurePath
from typing import TypeVar

from dataclasses import replace

from slice.model.patch_image_config import PatchImageConfig
from slice.model.patch_image_source_config import PatchImageSourceConfig


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