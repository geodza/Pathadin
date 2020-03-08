from typing import NamedTuple, Optional


class SlidePath(NamedTuple):
    slide_path: str
    annotations_path: Optional[str] = None