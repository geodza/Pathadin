from typing import Optional, List, Iterable

from dataclasses import dataclass, field

from slice.model.patch_image_config import PatchImageConfig


@dataclass
class PatchImageSourceConfig(PatchImageConfig):
    grid_length: int = 256
    stride: Optional[int] = None
    dependents: List[PatchImageConfig] = field(default_factory=list)


PatchImageSourceConfigIterable = Iterable[PatchImageSourceConfig]
