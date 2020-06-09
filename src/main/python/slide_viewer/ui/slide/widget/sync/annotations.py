from PyQt5.QtCore import QPoint
from PyQt5.QtGui import QColor

from annotation.annotation_type import AnnotationType
from annotation.model import AnnotationModel, AnnotationGeometry, TreeViewConfig
from common.dict_utils import format_map
from common_qt.util.debounce import qt_debounce
from common_qt.util.qobjects_convert_util import qpoint_to_ituple, ituples_to_qpoints, ituple_to_qpoint
from common_qt.util.slot_disconnected_utils import slot_disconnected
from slide_viewer.ui.slide.graphics.item.annotation.annotation_figure_graphics_item import \
	AnnotationFigurePathGraphicsItemDto
from slide_viewer.ui.slide.graphics.item.annotation.annotation_graphics_item import AnnotationTextGraphicsItemDto, \
	AnnotationGraphicsItemDto, AnnotationFigureGraphicsItemDto
from slide_viewer.ui.slide.graphics.view.graphics_view import GraphicsView
from slide_viewer.ui.slide.graphics.view.graphics_view_annotation_service3 import GraphicsViewAnnotationService3
from slide_viewer.ui.slide.widget.annotation.annotation_service import AnnotationService


def sync_filtered_annotation_graphics_item_and_model_annotations(view: GraphicsView,
																 model_service: AnnotationService) -> None:
	@qt_debounce(0.1)
	def on_model_edited(id_: str, model: AnnotationModel):
		if view.filter_graphics_item:
			view.filter_graphics_item.update()

	model_service.edited_signal().connect(on_model_edited)


def sync_graphics_and_model_annotations(graphics_service: GraphicsViewAnnotationService3,
										model_service: AnnotationService) -> None:
	def on_model_added(model: AnnotationModel):
		if model.id not in graphics_service.scene().annotations:
			graphics_model = build_annotation_graphics_item_dto(model)
			graphics_service.add_item(graphics_model)

	def on_model_edited(id_: str, model: AnnotationModel):
		graphics_model = build_annotation_graphics_item_dto(model)
		with slot_disconnected(graphics_service.signals.annotationLastPointChanged, on_last_point_changed), \
			 slot_disconnected(graphics_service.signals.annotationPointAdded, on_point_added), \
			 slot_disconnected(graphics_service.signals.annotationPosChanged, on_pos_changed), \
			 slot_disconnected(model_service.edited_signal(), on_model_edited):
			if graphics_service.has_item(id_):
				graphics_service.edit_item(id_, graphics_model)

	def on_models_deleted(ids: list):
		with slot_disconnected(graphics_service.signals.annotationRemovedFromScene, on_removed_from_scene):
			graphics_service.remove_from_scene(ids)

	def on_annotation_started(annotation_type: AnnotationType, p: QPoint):
		start_point = qpoint_to_ituple(p)
		geometry = AnnotationGeometry(annotation_type=annotation_type, origin_point=(0, 0),
									  points=[start_point, start_point])
		tree_view_config = TreeViewConfig(display_pattern='{label}',
										  decoration_attr='figure_graphics_view_config.color')
		annotation_model = AnnotationModel(geometry=geometry, id="", label="",
										   tree_view_config=tree_view_config)
		annotation_model = model_service.add(annotation_model)
		# We connect on_model_added to added_signal as synchronous callback => on_model_added has been called and item has been added to scene
		graphics_service.set_ongoing_annotation(annotation_model.id)

	def on_last_point_changed(id_: str, p: QPoint):
		# Do not debounce this callback. It must be called in right order with on_point_added.
		# Qt signal direct connection guarantees that callbacks will be called in synchronous manner.
		with slot_disconnected(model_service.edited_signal(), on_model_edited):
			model_service.edit_last_point(id_, qpoint_to_ituple(p))

	def on_point_added(id_: str, p: QPoint):
		# Do not debounce this callback. It must be called in right order with on_last_point_changed.
		# Qt signal direct connection guarantees that callbacks will be called in synchronous manner.
		with slot_disconnected(model_service.edited_signal(), on_model_edited):
			model_service.add_point(id_, qpoint_to_ituple(p))

	def on_pos_changed(id_: str, p: QPoint):
		with slot_disconnected(model_service.edited_signal(), on_model_edited):
			if model_service.has(id_):
				# Need to check if annotation is present because it can be deleted during qt_debounce time.
				model_service.edit_origin_point(id_, qpoint_to_ituple(p))

	def on_removed_from_scene(id_: str):
		with slot_disconnected(model_service.deleted_signal(), on_models_deleted):
			model_service.delete([id_])

	graphics_service.signals.annotationStarted.connect(on_annotation_started)
	graphics_service.signals.annotationLastPointChanged.connect(on_last_point_changed)
	graphics_service.signals.annotationPointAdded.connect(on_point_added)
	graphics_service.signals.annotationRemovedFromScene.connect(on_removed_from_scene)
	graphics_service.signals.annotationPosChanged.connect(on_pos_changed)

	model_service.added_signal().connect(on_model_added)
	model_service.edited_signal().connect(on_model_edited)
	model_service.deleted_signal().connect(on_models_deleted)


def build_annotation_text_graphics_item_dto(model: AnnotationModel) -> AnnotationTextGraphicsItemDto:
	display_pattern = model.text_graphics_view_config.display_pattern
	model_dict = model.dict(exclude_none=True)
	text = format_map(display_pattern, model_dict, joiner='<br/>')
	return AnnotationTextGraphicsItemDto(text, QColor(model.text_graphics_view_config.background_color))


def build_annotation_graphics_item_dto(m: AnnotationModel) -> AnnotationGraphicsItemDto:
	text_item_dto = build_annotation_text_graphics_item_dto(m)
	color = QColor(m.figure_graphics_view_config.color)
	figure_path_item_dto = AnnotationFigurePathGraphicsItemDto(m.geometry.annotation_type,
															   ituples_to_qpoints(m.geometry.points))
	figure_item_dto = AnnotationFigureGraphicsItemDto(figure_path_item_dto, color)
	return AnnotationGraphicsItemDto(m.id, ituple_to_qpoint(m.geometry.origin_point), figure_item_dto, text_item_dto,
									 m.figure_graphics_view_config.hidden, m.text_graphics_view_config.hidden)
