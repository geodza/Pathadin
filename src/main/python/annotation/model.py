import collections
import typing
from collections import OrderedDict
from typing import ClassVar, Optional, List, Tuple

from pydantic import BaseModel

from annotation.annotation_type import AnnotationType
from filter.common.filter_model import FilterResults


class TreeViewConfig(BaseModel):
	snake_case_name: ClassVar = 'tree_view_config'
	display_pattern: Optional[str]
	decoration_attr: Optional[str]
	decoration_size: Optional[int]


class TextGraphicsViewConfig(BaseModel):
	snake_case_name: ClassVar = 'text_graphics_view_config'
	display_pattern: str = '{label}\\n{stats[text]}\\n{filter_results[text]}'
	# display_pattern: str = '{label}\\n{stats[text]}\\n{filter_results[text]}'
	hidden: bool = False
	background_color: str = '#32cd32'


class FigureGraphicsViewConfig(BaseModel):
	snake_case_name: ClassVar = 'figure_graphics_view_config'
	hidden: bool = False
	color: str = '#32cd32'


class AnnotationGeometry(BaseModel):
	annotation_type: AnnotationType
	origin_point: Tuple[int, int]
	points: List[Tuple[int, int]]


class AnnotationStats(BaseModel):
	# __slots__ = ['area', 'area_px', 'length', 'length_px', 'prop2']  # for pycharm hints only
	text: Optional[str]
	area: Optional[int]
	area_px: Optional[int]
	area_text: Optional[str]
	length: Optional[int]
	length_px: Optional[int]
	length_text: Optional[str]


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
	filter_results: Optional[FilterResults] = None
	user_attrs: OrderedDict = OrderedDict()


class AnnotationTreeItems(BaseModel):
	annotations: typing.Dict[str, AnnotationModel]


class B(BaseModel):
	bb: str


class P(BaseModel):
	a: str
	b: B


if __name__ == '__main__':
	b = B(bb="2")
	p = P(a="1", b=b)
	pd = p.dict()
	pdr = P.parse_obj(pd)
	assert p == pdr

	t = ("1", 2)
	d = dict([t])
	m = AnnotationModel(geometry=AnnotationGeometry(annotation_type=AnnotationType.RECT, origin_point=(0, 0),
													points=[(0, 0), (10, 10)]), id="1")
	d = m.dict()
	s = "annotation_{id}_{geometry[annotation_type]}_{geometry[points][0][0]}".format_map(m.dict())
	print(s)
	print(hasattr(m, '__hash__'))
	print(isinstance(m, collections.Hashable))
	print(hash(m))
