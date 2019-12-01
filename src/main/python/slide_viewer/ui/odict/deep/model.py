import typing
from collections import OrderedDict
from typing import ClassVar, Optional

from pydantic import BaseModel

from slide_viewer.ui.slide.graphics.item.annotation.model import AnnotationGeometry, TextGraphicsViewConfig, \
    FigureGraphicsViewConfig, AnnotationStats


class TreeViewConfig(BaseModel):
    snake_case_name: ClassVar = 'tree_view_config'
    display_attrs: Optional[list]
    decoration_attr: Optional[str]


def default_tree_view_config_factory():
    return TreeViewConfig(display_attrs=['name'], decoration_attr='annotation_graphics_view_config.figure_color')


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
