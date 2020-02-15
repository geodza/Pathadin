from typing import Optional

from dataclasses import dataclass, field


@dataclass
class PatchImageConfig:
    slide_path: str
    level: int
    annotations_path: Optional[str] = None
    offset_x: int = 0
    offset_y: int = 0
    metadata: dict = field(default_factory=dict)