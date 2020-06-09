from typing import NamedTuple, Optional, Tuple

from annotation.annotation_type import AnnotationType

ituple = Tuple[int, int]
ituples = Tuple[ituple, ...]


class RegionData(NamedTuple):
	img_path: str
	level: Optional[int] = None
	origin_point: Optional[ituple] = None
	points: Optional[ituples] = None
	annotation_type: AnnotationType = AnnotationType.RECT
