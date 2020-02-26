from typing import Optional, List, Iterable, Tuple

from dataclasses import dataclass, field

from slice.model.patch_image_config import PatchImageConfig


@dataclass
class PatchImageSourceConfig(PatchImageConfig):
    patch_size: Tuple[int, int]=(256,256)
    stride_x: Optional[int] = None
    stride_y: Optional[int] = None
    dependents: List[PatchImageConfig] = field(default_factory=list)


PatchImageSourceConfigIterable = Iterable[PatchImageSourceConfig]
