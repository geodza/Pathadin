from typing import List

from PyQt5.QtCore import QPoint
from dataclasses import replace

from slide_viewer.ui.slide.graphics.item.annotation.annotation_graphics_item import AnnotationGraphicsItem


def set_points(item: AnnotationGraphicsItem, points: List[QPoint]) -> None:
	figure_item_dto = item.figure_item_dto
	path_item_dto = figure_item_dto.path_item_dto
	new_path_item_dto = replace(path_item_dto, points=points)
	new_figure_item_dto = replace(figure_item_dto, path_item_dto=new_path_item_dto)
	item.set_figure_item_dto(new_figure_item_dto)


class AnnotationGraphicsItemService:
	# graphics_item_provider:Callable[[str],AnnotationGraphicsItem]

	@classmethod
	def edit_last_point(cls, item: AnnotationGraphicsItem, p: QPoint) -> None:
		new_points = list(item.figure_item_dto.path_item_dto.points)
		new_points[-1] = p
		set_points(item, new_points)

	@classmethod
	def add_point(cls, item: AnnotationGraphicsItem, p: QPoint) -> None:
		new_points = list(item.figure_item_dto.path_item_dto.points)
		new_points.append(p)
		set_points(item, new_points)
