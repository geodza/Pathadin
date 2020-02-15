from pathlib import PurePath
from typing import TypeVar

from dataclasses import replace

#
# @dataclass
# class SlideSliceConfig:
#     slide_path: str
#     level: int
#     grid_length: int
#     annotations_path: Optional[str] = None
#     offset_x: int = 0
#     offset_y: int = 0
#     stride: Optional[int] = None

from slice.patch_image_config import PatchImageConfig
from slice.patch_image_source_config import PatchImageSourceConfig


# @dataclass
# class PartialImageSourceConfig(PatchImageSourceConfig):
#     slide_path: Optional[str] = None
#     level: Optional[int] = None
#     annotations_path: Optional[str] = None
#     offset_x: Optional[int] = None
#     offset_y: Optional[int] = None
#     grid_length: Optional[int] = None
#     stride: Optional[int] = None
#
#
# @dataclass
# class PartialImageSourceConfig(PartialImageSourceConfig)
#     dependents: Optional[List[PartialImageSourceConfig2]] = None
#     inheritors: Optional[List[PartialImageSourceConfig2]] = None


# @dataclass
# class PatchImageTemplateConfig:
#     template: PatchImageConfig
#     variations: List[PatchImageConfig]


# @dataclass
# class PatchImageFlowConfig:
#     source: List[PatchImageSourceConfig]
#     dependents: int


# @dataclass
# class ObjectTemplate:
#     template: Any
#     variations: List[Any]


# # @dataclass
# class A(NamedTuple):
#     field1: int
#
#
# # @dataclass
# class B(A, NamedTuple):
#     field1: Optional[int] = None
#
#
# if __name__ == '__main__':
#     a, b, c = A(123), B(), B(456)
#     print(a, b, c)
#     Af, Bf = fields(A), fields(B)
#     print(Af, Bf)
#     af, bf = fields(a), fields(b)
#     print(af, bf)
#     pass


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