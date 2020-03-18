import typing

from PyQt5.QtCore import pyqtSignal, QPoint, QObject
from PyQt5.QtGui import QVector2D
from dataclasses import dataclass, field

from common_qt.debounce_signal import debounce_two_arg_slot_wrap
from common_qt.qobjects_convert_util import qpoint_to_ituple, ituple_to_qpoint
from common_qt.slot_disconnected_utils import slot_disconnected
from slide_viewer.ui.common.annotation_type import AnnotationType
from slide_viewer.ui.common.model import TreeViewConfig, AnnotationModel, AnnotationGeometry
from slide_viewer.ui.slide.graphics.graphics_scene import GraphicsScene
from slide_viewer.ui.slide.graphics.item.annotation.annotation_graphics_item import AnnotationGraphicsItem
from slide_viewer.ui.slide.graphics.view.graphics_annotation_utils import build_annotation_graphics_model
from slide_viewer.ui.slide.slide_stats_provider import SlideStatsProvider
from slide_viewer.ui.slide.widget.annotation_stats_processor import AnnotationStatsProcessor
from slide_viewer.ui.slide.widget.interface.annotation_pixmap_provider import AnnotationItemPixmapProvider
from slide_viewer.ui.slide.widget.interface.annotation_service import AnnotationService
from slide_viewer.ui.slide.widget.interface.scale_view_provider import ScaleProvider


class GraphicsViewAnnotationServiceSignals(QObject):
    annotationIsInProgressChanged = pyqtSignal(bool)
    annotationRemovedFromScene = pyqtSignal(str)

    def __init__(self, parent: typing.Optional[QObject] = None) -> None:
        super().__init__(parent)


@dataclass
class GraphicsViewAnnotationService:
    scene_provider: typing.Callable[[], GraphicsScene]
    annotation_service: AnnotationService
    annotation_pixmap_provider: AnnotationItemPixmapProvider
    annotation_stats_processor: AnnotationStatsProcessor
    scale_provider: ScaleProvider
    slide_stats_provider: SlideStatsProvider
    points_closeness_factor: float = 10
    annotation_type: typing.Optional[AnnotationType] = None
    annotation: typing.Optional[AnnotationGraphicsItem] = None
    signals: GraphicsViewAnnotationServiceSignals = field(default_factory=GraphicsViewAnnotationServiceSignals)

    def scene(self) -> GraphicsScene:
        return self.scene_provider()

    def __post_init__(self):
        self.on_pos_changed = debounce_two_arg_slot_wrap(0.1)(self.on_pos_changed)
        self.annotation_service.added_signal().connect(self.on_annotation_model_added)
        self.annotation_service.edited_signal().connect(self.on_annotation_model_edited)
        self.annotation_service.deleted_signal().connect(self.on_annotation_models_deleted)
        self.signals.annotationRemovedFromScene.connect(self.__on_annotation_removed_from_scene)
        # self.scene().annotationModelsSelected.connect(self.on_scene_annotations_selected)

    def __on_annotation_removed_from_scene(self, id_: str):
        with slot_disconnected(self.annotation_service.deleted_signal(), self.on_annotation_models_deleted):
            self.annotation_service.delete([id_])

    def on_annotation_models_deleted(self, ids: typing.List[str]):
        with slot_disconnected(self.signals.annotationRemovedFromScene, self.__on_annotation_removed_from_scene):
            self.scene().remove_annotations(ids)

    def on_annotation_model_added(self, annotation_model: AnnotationModel):
        # print("on_annotation_model_added", annotation_model)
        annotation = self.create_item_from_model(annotation_model)
        self.scene().add_annotation(annotation)

    def on_annotation_model_edited(self, id_: str, annotation_model: AnnotationModel):
        # print(f"on_annotation_model_edited: {id(self)}")
        with slot_disconnected(self.annotation_service.edited_signal(), self.on_annotation_model_edited):
            stats = self.annotation_stats_processor.calc_stats(annotation_model)
            self.annotation_service.edit_stats(id_, stats)

        item = self.scene().annotations.get(id_)
        item_model = build_annotation_graphics_model(annotation_model)
        with slot_disconnected(item.signals.posChanged, self.on_pos_changed):
            item.set_model(item_model)

    def create_item_from_model(self, annotation_model: AnnotationModel):
        annotation = AnnotationGraphicsItem(id=annotation_model.id, scale_provider=self.scale_provider,
                                            model=build_annotation_graphics_model(annotation_model),
                                            is_in_progress=False,
                                            slide_stats_provider=self.slide_stats_provider)

        def __on_removed_from_scene(id_: str):
            self.signals.annotationRemovedFromScene.emit(id_)

        annotation.signals.posChanged.connect(self.on_pos_changed)
        annotation.signals.removedFromScene.connect(__on_removed_from_scene)
        return annotation

    def on_pos_changed(self, id_: str, p: QPoint):
        # print(f'__on_pos_changed: {self.id}')
        # annotation.update()
        item = self.scene().annotations.get(id_)
        # item.update()
        # with slot_disconnected(self.annotation_service.edited_signal(), self.on_annotation_model_edited):
        self.annotation_service.edit_origin_point(id_, qpoint_to_ituple(p))

    def start_annotation(self, p: QPoint) -> None:
        self.on_off_annotation()
        start_point = qpoint_to_ituple(p)
        geometry = AnnotationGeometry(annotation_type=self.annotation_type, origin_point=(0, 0),
                                      points=[start_point, start_point])
        tree_view_config = TreeViewConfig(display_attrs=['label'],
                                          decoration_attr='figure_graphics_view_config.color')
        # annotation_id = self.scene().get_next_annotation_id()
        # annotation_label = self.annotation_label_template.format(annotation_id)
        annotation_model = AnnotationModel(geometry=geometry, id="", label="",
                                           tree_view_config=tree_view_config)
        with slot_disconnected(self.annotation_service.added_signal(), self.on_annotation_model_added):
            annotation_model = self.annotation_service.add(annotation_model)

        self.annotation = self.create_item_from_model(annotation_model)
        self.scene().add_annotation(self.annotation)
        # self.annotation: AnnotationGraphicsItem = self.scene().add_annotation(self.annotation_model)
        self.annotation.is_in_progress = True
        # self.setMouseTracking(True)
        self.annotation.update()

    def finish_annotation(self) -> None:
        annotation_model = self.annotation_service.get(self.annotation.id)
        if not annotation_model.geometry.is_distinguishable_from_point():
            self.scene().remove_annotations([self.annotation.id])
            # self.scene().removeItem(self.annotation)
        elif self.annotation_type == AnnotationType.POLYGON:
            self.close_polygon()

        self.annotation.is_in_progress = False
        self.annotation.update()
        self.annotation = None
        self.on_off_annotation()

    def on_off_annotation(self) -> None:
        if self.annotation:
            id = self.annotation.id
            self.annotation = None
            # self.annotation_model = None
            self.scene().remove_annotations([id])
            # self.scene().removeItem(self.annotation)

    def edit_point(self, p: QPoint):
        if self.annotation_type == AnnotationType.POLYGON and self.is_polygon_about_to_be_closed(p):
            p = ituple_to_qpoint(self.annotation_service.get_first_point(self.annotation.id))
        self.annotation_service.edit_last_point(self.annotation.id, qpoint_to_ituple(p))
        self.annotation.update()

    def add_point_or_close_figure(self, p: QPoint):
        if self.annotation_type == AnnotationType.POLYGON:
            if self.is_polygon_about_to_be_closed(p):
                self.finish_annotation()
            else:
                self.annotation_service.add_point(self.annotation.id, qpoint_to_ituple(p))
        else:
            self.finish_annotation()

    def are_points_close(self, p1: QPoint, p2: QPoint) -> bool:
        length = QVector2D(p1 - p2).length()
        return length < self.points_closeness_factor / self.scale_provider.get_scale()

    def is_polygon_about_to_be_closed(self, p: QPoint) -> bool:
        first_point = self.annotation_service.get_first_point(self.annotation.id)
        return self.are_points_close(ituple_to_qpoint(first_point), p)

    def close_polygon(self):
        first_point = self.annotation_service.get_first_point(self.annotation.id)
        self.annotation_service.edit_last_point(self.annotation.id, first_point)

    def delete_selected(self):
        annotations_to_remove = [i for i in self.scene().annotations.values() if i.isSelected()]
        for annotation in annotations_to_remove:
            self.scene().removeItem(annotation)

    def is_active(self):
        return bool(self.annotation_type)

    def is_in_progress(self):
        return bool(self.annotation)

    def mouse_move(self, p: QPoint) -> None:
        if self.annotation:
            self.edit_point(p)

    def mouse_click(self, p: QPoint):
        if self.annotation:
            self.add_point_or_close_figure(p)
        else:
            self.start_annotation(p)

    def on_enter_press(self) -> None:
        if self.annotation:
            self.finish_annotation()

    def on_esc_press(self):
        if self.annotation:
            self.on_off_annotation()

    def on_delete_press(self):
        if self.annotation:
            self.on_off_annotation()
        else:
            self.delete_selected()
