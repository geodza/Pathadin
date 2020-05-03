import collections
import typing
from collections import OrderedDict
from typing import ClassVar, Optional, List, Tuple

from pydantic import BaseModel

from slide_viewer.ui.common.annotation_type import AnnotationType


class TreeViewConfig(BaseModel):
	snake_case_name: ClassVar = 'tree_view_config'
	display_attrs: Optional[list]
	decoration_attr: Optional[str]


def default_tree_view_config_factory():
	return TreeViewConfig(display_attrs=['name'], decoration_attr='annotation_graphics_view_config.figure_color')


class TextGraphicsViewConfig(BaseModel):
	snake_case_name: ClassVar = 'text_graphics_view_config'
	display_attrs: List[str] = ['label']
	hidden: bool = False
	background_color: str = '#32cd32'


class FigureGraphicsViewConfig(BaseModel):
	snake_case_name: ClassVar = 'figure_graphics_view_config'
	hidden: bool = False
	color: str = '#32cd32'


def are_points_distinguishable(points: List):
	return len(points) >= 2 and points[0] != points[1]


class AnnotationGeometry(BaseModel):
	annotation_type: AnnotationType
	origin_point: Tuple[int, int]
	points: List[Tuple[int, int]]

	def is_distinguishable_from_point(self) -> bool:
		return are_points_distinguishable(self.points)


class AnnotationStats(BaseModel):
	# __slots__ = ['area', 'area_px', 'length', 'length_px', 'prop2']  # for pycharm hints only
	area: Optional[int]
	area_px: Optional[int]
	area_text: Optional[str]
	length: Optional[int]
	length_px: Optional[int]
	length_text: Optional[str]


# dd: OrderedDict = OrderedDict()
# prop2: int = attr.ib()


class AnnotationModel(BaseModel):
	geometry: AnnotationGeometry
	id: str
	label: Optional[str]
	tree_view_config: TreeViewConfig = TreeViewConfig()
	text_graphics_view_config: TextGraphicsViewConfig = TextGraphicsViewConfig()
	figure_graphics_view_config: FigureGraphicsViewConfig = FigureGraphicsViewConfig()
	stats: AnnotationStats = None
	filter_id: str = None
	filter_level: Optional[int] = None
	filter_results: OrderedDict = None
	user_attrs: OrderedDict = OrderedDict()

class AnnotationTreeItems(BaseModel):
	annotations: typing.Dict[str, AnnotationModel]


if __name__ == '__main__':
	m = AnnotationModel(geometry=AnnotationGeometry(annotation_type=AnnotationType.RECT, origin_point=(0, 0),
													points=[(0, 0), (10, 10)]), id="1")
	print(hasattr(m, '__hash__'))
	print(isinstance(m, collections.Hashable))
	print(hash(m))
