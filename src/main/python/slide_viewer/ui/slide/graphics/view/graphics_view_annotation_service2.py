from typing import List, Optional, Callable

from PyQt5.QtCore import pyqtSignal, QPoint, QObject, QEvent, Qt
from PyQt5.QtGui import QVector2D
from PyQt5.QtWidgets import QGraphicsSceneMouseEvent
from dataclasses import dataclass, field

from common_qt.debounce_signal import debounce_two_arg_slot_wrap
from common_qt.key_press_util import KeyPressEventUtil
from common_qt.qobjects_convert_util import qpoint_to_ituple, ituple_to_qpoint
from common_qt.slot_disconnected_utils import slot_disconnected
from slide_viewer.ui.common.annotation_type import AnnotationType
from slide_viewer.ui.common.model import TreeViewConfig, AnnotationModel, AnnotationGeometry
from slide_viewer.ui.slide.graphics.graphics_scene import GraphicsScene
from slide_viewer.ui.slide.graphics.item.annotation.annotation_graphics_item import AnnotationGraphicsItem
from slide_viewer.ui.slide.graphics.view.graphics_annotation_utils import build_annotation_graphics_model
from slide_viewer.ui.slide.widget.interface.annotation_service import AnnotationService
from slide_viewer.ui.slide.widget.interface.scale_view_provider import ScaleProvider


class GraphicsViewAnnotationServiceSignals(QObject):
    annotationRemovedFromScene = pyqtSignal(str)

    def __init__(self, parent: Optional[QObject] = None) -> None:
        super().__init__(parent)


@dataclass
class GraphicsViewAnnotationService2:
    scene_provider: Callable[[], GraphicsScene]
    annotation_service: AnnotationService
    scale_provider: ScaleProvider
    points_closeness_factor: float = 10
    annotation_type: Optional[AnnotationType] = None
    ongoing_annotation: Optional[AnnotationGraphicsItem] = None
    signals: GraphicsViewAnnotationServiceSignals = field(default_factory=GraphicsViewAnnotationServiceSignals)

    def scene(self) -> GraphicsScene:
        return self.scene_provider()

    def __post_init__(self):
        self.on_pos_changed = debounce_two_arg_slot_wrap(0.1)(self.on_pos_changed)
        self.annotation_service.added_signal().connect(self.on_model_added)
        self.annotation_service.edited_signal().connect(self.on_model_edited)
        self.annotation_service.deleted_signal().connect(self.on_models_deleted)
        self.signals.annotationRemovedFromScene.connect(self.__on_removed_from_scene)
        # self.scene().annotationModelsSelected.connect(self.on_scene_annotations_selected)

    def on_pos_changed(self, id_: str, p: QPoint):
        self.annotation_service.edit_origin_point(id_, qpoint_to_ituple(p))

    def on_model_added(self, annotation_model: AnnotationModel):
        # print("on_annotation_model_added", annotation_model)
        annotation = self.create_item_from_model(annotation_model)
        self.scene().add_annotation(annotation)

    def on_model_edited(self, id_: str, annotation_model: AnnotationModel):
        graphics_model = build_annotation_graphics_model(annotation_model)
        graphics_item = self.scene().annotations.get(id_)
        graphics_item.set_model(graphics_model)

    def on_models_deleted(self, ids: List[str]):
        with slot_disconnected(self.signals.annotationRemovedFromScene, self.__on_removed_from_scene):
            self.scene().remove_annotations(ids)

    def __on_removed_from_scene(self, id_: str):
        with slot_disconnected(self.annotation_service.deleted_signal(), self.on_models_deleted):
            self.annotation_service.delete([id_])

    def create_item_from_model(self, annotation_model: AnnotationModel) -> AnnotationGraphicsItem:
        annotation = AnnotationGraphicsItem(id=annotation_model.id,
                                            scale_provider=self.scale_provider,
                                            model=build_annotation_graphics_model(annotation_model),
                                            is_in_progress=False)

        def __on_removed_from_scene(id_: str):
            self.signals.annotationRemovedFromScene.emit(id_)

        annotation.signals.posChanged.connect(self.on_pos_changed)
        annotation.signals.removedFromScene.connect(__on_removed_from_scene)
        return annotation

    def start_annotation(self, p: QPoint) -> None:
        start_point = qpoint_to_ituple(p)
        geometry = AnnotationGeometry(annotation_type=self.annotation_type, origin_point=(0, 0),
                                      points=[start_point, start_point])
        tree_view_config = TreeViewConfig(display_attrs=['label'],
                                          decoration_attr='figure_graphics_view_config.color')
        # annotation_id = self.scene().get_next_annotation_id()
        # annotation_label = self.annotation_label_template.format(annotation_id)
        annotation_model = AnnotationModel(geometry=geometry, id="", label="",
                                           tree_view_config=tree_view_config)
        with slot_disconnected(self.annotation_service.added_signal(), self.on_model_added):
            annotation_model = self.annotation_service.add(annotation_model)

        self.ongoing_annotation = self.create_item_from_model(annotation_model)
        self.scene().add_annotation(self.ongoing_annotation)
        self.ongoing_annotation.is_in_progress = True
        self.ongoing_annotation.update()

    def cancel_annotation_if_any(self) -> None:
        if self.ongoing_annotation:
            self.scene().remove_annotations([self.ongoing_annotation.id])
            self.ongoing_annotation = None

    def finish_annotation(self) -> None:
        annotation_model = self.annotation_service.get(self.ongoing_annotation.id)
        if not annotation_model.geometry.is_distinguishable_from_point():
            self.scene().remove_annotations([self.ongoing_annotation.id])
            # self.scene().removeItem(self.annotation)
        elif self.annotation_type == AnnotationType.POLYGON:
            self.close_polygon()

        self.ongoing_annotation.is_in_progress = False
        self.ongoing_annotation.update()
        self.ongoing_annotation = None

    def edit_last_point(self, p: QPoint) -> None:
        if self.annotation_type == AnnotationType.POLYGON and self.is_polygon_about_to_be_closed(p):
            p = ituple_to_qpoint(self.annotation_service.get_first_point(self.ongoing_annotation.id))
        self.annotation_service.edit_last_point(self.ongoing_annotation.id, qpoint_to_ituple(p))

    def add_point_or_close_figure(self, p: QPoint) -> None:
        if self.annotation_type == AnnotationType.POLYGON:
            if self.is_polygon_about_to_be_closed(p):
                self.finish_annotation()
            else:
                self.annotation_service.add_point(self.ongoing_annotation.id, qpoint_to_ituple(p))
        else:
            self.finish_annotation()

    def are_points_close(self, p1: QPoint, p2: QPoint) -> bool:
        length = QVector2D(p1 - p2).length()
        return length < self.points_closeness_factor / self.scale_provider.get_scale()

    def is_polygon_about_to_be_closed(self, p: QPoint) -> bool:
        first_point = self.annotation_service.get_first_point(self.ongoing_annotation.id)
        return self.are_points_close(ituple_to_qpoint(first_point), p)

    def close_polygon(self) -> None:
        first_point = self.annotation_service.get_first_point(self.ongoing_annotation.id)
        self.annotation_service.edit_last_point(self.ongoing_annotation.id, first_point)

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
                    self.edit_last_point(event.scenePos())
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
                        p = event.scenePos()
                        if self.ongoing_annotation:
                            self.add_point_or_close_figure(p)
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
