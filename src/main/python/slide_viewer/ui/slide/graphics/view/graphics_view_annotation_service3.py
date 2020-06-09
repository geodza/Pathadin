from typing import Optional, Callable, List

from PyQt5.QtCore import pyqtSignal, QPoint, QObject, QEvent, Qt
from PyQt5.QtGui import QVector2D
from PyQt5.QtWidgets import QGraphicsSceneMouseEvent
from dataclasses import dataclass, field

from annotation.annotation_type import AnnotationType
from common.log_utils import log
from common_qt.util.key_press_util import KeyPressEventUtil
from slide_viewer.ui.slide.graphics.graphics_scene import GraphicsScene
from slide_viewer.ui.slide.graphics.item.annotation.annotation_graphics_item import AnnotationGraphicsItem, \
	AnnotationGraphicsItemDto
from slide_viewer.ui.slide.graphics.view.annotation_graphics_item_service import AnnotationGraphicsItemService
from slide_viewer.ui.slide.widget.interface.scale_view_provider import ScaleProvider


class GraphicsViewAnnotationServiceSignals3(QObject):
	# annotationAddedToScene signal is absent because GraphicsViewAnnotationService3 doesnt know how to create annotation.
	# Even if it would know how to create new AnnotationGraphicsItemDto then parent would need to know
	# how to convert this new graphics item -> annotation model to add it to annotation service.
	annotationRemovedFromScene = pyqtSignal(str)
	annotationPosChanged = pyqtSignal(str, QPoint)
	annotationLastPointChanged = pyqtSignal(str, QPoint)
	annotationPointAdded = pyqtSignal(str, QPoint)
	annotationStarted = pyqtSignal(AnnotationType, QPoint)

	def __init__(self, parent: Optional[QObject] = None) -> None:
		super().__init__(parent)


@dataclass
class GraphicsViewAnnotationService3:
	scene_provider: Callable[[], GraphicsScene]
	scale_provider: ScaleProvider
	points_closeness_factor: float = 10
	annotation_type: Optional[AnnotationType] = None
	ongoing_annotation: Optional[AnnotationGraphicsItem] = None
	signals: GraphicsViewAnnotationServiceSignals3 = field(default_factory=GraphicsViewAnnotationServiceSignals3)

	def __post_init__(self):
		pass

	def scene(self) -> GraphicsScene:
		return self.scene_provider()

	def add_item(self, dto: AnnotationGraphicsItemDto):
		graphics_item = AnnotationGraphicsItem(id=dto.id,
											   scale_provider=self.scale_provider,
											   _pos=dto.pos,
											   _figure_item_dto=dto.figure_item_dto,
											   _figure_hidden=dto.figure_hidden,
											   _text_item_dto=dto.text_item_dto,
											   _text_hidden=dto.text_hidden,
											   _is_in_progress=False)
		graphics_item.signals.posChanged.connect(self.signals.annotationPosChanged)
		graphics_item.signals.removedFromScene.connect(self.signals.annotationRemovedFromScene)
		self.scene().add_annotation(graphics_item)

	def has_item(self, id_: str) -> bool:
		return id_ in self.scene().annotations

	def edit_item(self, id_: str, dto: AnnotationGraphicsItemDto):
		graphics_item = self.scene().annotations.get(id_)
		graphics_item.set_pos(dto.pos)
		graphics_item.set_figure_item_dto(dto.figure_item_dto)
		graphics_item.set_figure_hidden(dto.figure_hidden)
		graphics_item.set_text_item_dto(dto.text_item_dto)
		graphics_item.set_text_hidden(dto.text_hidden)

	def start_annotation(self, p: QPoint) -> None:
		self.signals.annotationStarted.emit(self.annotation_type, p)

	def cancel_annotation_if_any(self) -> None:
		if self.ongoing_annotation:
			id_ = self.ongoing_annotation.id
			self.ongoing_annotation = None
			self.scene().remove_annotations([id_])

	def finish_annotation(self) -> None:
		if not self.ongoing_annotation.is_distinguishable_from_point():
			id_ = self.ongoing_annotation.id
			self.ongoing_annotation = None
			# be careful with signals so we set None before removing
			self.scene().remove_annotations([id_])
		else:
			if self.annotation_type == AnnotationType.POLYGON:
				self.close_polygon()
			self.ongoing_annotation.set_is_in_progress(False)
			self.ongoing_annotation = None

	def set_ongoing_annotation(self, id_: str) -> None:
		item = self.scene().annotations[id_]
		item.set_is_in_progress(False)
		self.ongoing_annotation = item

	def edit_last_point(self, id_: str, p: QPoint) -> None:
		item = self.scene().annotations[id_]
		AnnotationGraphicsItemService.edit_last_point(item, p)
		self.signals.annotationLastPointChanged.emit(id_, p)

	def add_point_or_finish(self, p: QPoint) -> None:
		if self.annotation_type == AnnotationType.POLYGON:
			if self.is_polygon_about_to_be_closed(p):
				self.finish_annotation()
			else:
				AnnotationGraphicsItemService.add_point(self.ongoing_annotation, p)
				self.signals.annotationPointAdded.emit(self.ongoing_annotation.id, p)
		else:
			self.finish_annotation()

	def are_points_close(self, p1: QPoint, p2: QPoint) -> bool:
		length = QVector2D(p1 - p2).length()
		return length < self.points_closeness_factor / self.scale_provider.get_scale()

	def is_polygon_about_to_be_closed(self, p: QPoint) -> bool:
		first_point = self.ongoing_annotation.figure_item_dto.path_item_dto.points[0]
		return self.are_points_close(first_point, p)

	def close_polygon(self) -> None:
		first_point = self.ongoing_annotation.figure_item_dto.path_item_dto.points[0]
		self.edit_last_point(self.ongoing_annotation.id, first_point)

	def remove_from_scene(self, ids: List[str]):
		self.scene().remove_annotations(ids)

	def delete_selected(self) -> None:
		annotations_to_remove = [i for i in self.scene().annotations.values() if i.isSelected()]
		for annotation in annotations_to_remove:
			self.scene().removeItem(annotation)

	def is_in_creation_mode(self) -> bool:
		return bool(self.annotation_type)

	def eventFilter(self, source: QObject, event: QEvent) -> bool:
		if KeyPressEventUtil.is_enter(event):
			if self.ongoing_annotation:
				self.finish_annotation()
				event.accept()
				return True
			else:
				return False
		elif KeyPressEventUtil.is_esc(event):
			if self.ongoing_annotation:
				self.cancel_annotation_if_any()
				event.accept()
				return True
			else:
				return False
		elif KeyPressEventUtil.is_delete(event):
			if self.ongoing_annotation:
				self.cancel_annotation_if_any()
			else:
				self.delete_selected()
			event.accept()
			return True
		elif isinstance(event, QGraphicsSceneMouseEvent):
			if event.type() == QEvent.GraphicsSceneMouseMove and not event.button():
				if self.ongoing_annotation:
					p = event.scenePos().toPoint()
					if self.annotation_type == AnnotationType.POLYGON and self.is_polygon_about_to_be_closed(p):
						first_point = self.ongoing_annotation.figure_item_dto.path_item_dto.points[0]
						p = first_point
					self.edit_last_point(self.ongoing_annotation.id, p)
					event.accept()
					return True
				else:
					return False
			elif event.type() == QEvent.GraphicsSceneMousePress:
				if self.is_in_creation_mode():
					# disable selection of items when in annotations creation mode
					event.accept()
					return True
				else:
					return False
			elif event.type() == QEvent.GraphicsSceneMouseRelease:
				if event.scenePos() == event.buttonDownScenePos(Qt.LeftButton):
					if self.is_in_creation_mode():
						p = event.scenePos().toPoint()
						if self.ongoing_annotation:
							self.add_point_or_finish(p)
						else:
							self.start_annotation(p)
						event.accept()
						return True
					else:
						return False
				else:
					return False
			else:
				return False
		else:
			return False
