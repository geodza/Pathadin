from typing import Optional

from dataclasses import dataclass, field


@dataclass
class PatchImageConfig:
    slide_path: str
    level: int
    target_color_mode: str = 'RGB'
    rescale_result_image: bool = True
    annotations_path: Optional[str] = None
    offset_x: int = 0
    offset_y: int = 0
    metadata: dict = field(default_factory=dict)
