import typing

from PyQt5 import QtGui
from PyQt5.QtCore import QObject, Qt, QPointF, pyqtSignal, QEvent, QPoint, QRectF, QTimer
from PyQt5.QtGui import QTransform, QVector2D, QMouseEvent, QWheelEvent, QResizeEvent, QCursor, QBrush
from PyQt5.QtWidgets import QGraphicsView, QWidget, QGraphicsSceneDragDropEvent
from dataclasses import dataclass, field, InitVar

from slide_viewer.common.debug_only_decorator import debug_only
from slide_viewer.common.slide_helper import SlideHelper
from slide_viewer.common_qt.abcq_meta import ABCQMeta
from slide_viewer.common_qt.almost_immediate_timer import AlmostImmediateTimer
from slide_viewer.common_qt.debounce_signal import debounce_three_arg_slot_wrap
from slide_viewer.common_qt.key_press_util import KeyPressEventUtil
from slide_viewer.common_qt.qobjects_convert_util import qpoint_to_ituple, \
    ituple_to_qpoint
from slide_viewer.common_qt.slot_disconnected_utils import slot_disconnected
from slide_viewer.ui.common.common import mime_data_is_url
from slide_viewer.ui.common.timeline.pan_time_line import PanTimeLine, PanTimeLineData
from slide_viewer.ui.common.timeline.scale_time_line import ScaleTimeLineData, ScaleTimeLine
from slide_viewer.ui.model.annotation_type import AnnotationType
from slide_viewer.ui.odict.deep.model import TreeViewConfig, AnnotationModel
from slide_viewer.ui.slide.graphics.graphics_scene import GraphicsScene, build_annotation_graphics_model
from slide_viewer.ui.slide.graphics.graphics_view_transform_notifier import GraphicsViewTransformNotifier
from slide_viewer.ui.slide.graphics.item.annotation.annotation_graphics_item import AnnotationGraphicsItem
from slide_viewer.ui.slide.graphics.item.annotation.model import AnnotationGeometry
from slide_viewer.ui.slide.graphics.item.debug.slide_graphics_debug_item_rect import SlideGraphicsDebugItemRect
from slide_viewer.ui.slide.graphics.item.debug.slide_graphics_debug_view_scene_rect import \
    SlideGraphicsDebugViewSceneRect
from slide_viewer.ui.slide.graphics.item.filter_graphics_item import FilterGraphicsItem
from slide_viewer.ui.slide.graphics.item.grid_graphics_item import GridGraphicsItem
from slide_viewer.ui.slide.graphics.item.slide_graphics_item import SlideGraphicsItem
from slide_viewer.ui.slide.slide_stats_provider import SlideStatsProvider
from slide_viewer.ui.slide.widget.annotation_stats_processor import AnnotationStatsProcessor
from slide_viewer.ui.slide.widget.interface import annotation_pixmap_provider
from slide_viewer.ui.slide.widget.interface.annotation_service import AnnotationService
from slide_viewer.ui.slide.widget.interface.scale_view_provider import ScaleProvider

help_text = "" \
            "Drag-n-drop an image file here\n" \
            "You can press Esc or Delete to cancel annotation creation\n" \
            "You can press Enter to finish annotation creation (useful for polygon closing)\n" \
            "You can select multiple annotations with mouse left-click while holding Ctrl\n" \
            "You can press Delete to delete selected annotations\n" \
            "You can press Ctrl+Tab to switch between sub windows\n" \
            "You can dock Annotations to different side of main window\n" \
            "You can undock Annotations to turn it into floating window\n" \
            " ... And another useful help"


@dataclass
class ViewParams:
    mouse_scene_pos: typing.Optional[QPointF] = None
    view_scene_top_left: typing.Optional[QPointF] = None
    view_scene_center: typing.Optional[QPointF] = None
    mouse_pos: typing.Optional[QPoint] = None
    mouse_move_between_press_and_release: bool = False


@dataclass
class GraphicsView(GraphicsViewTransformNotifier, ScaleProvider, SlideStatsProvider, metaclass=ABCQMeta):
    annotation_service: AnnotationService
    pixmap_provider: annotation_pixmap_provider
    annotation_stats_processor: AnnotationStatsProcessor
    parent_: InitVar[typing.Optional[QWidget]] = field(default=None)
    fit_scale: float = 1
    min_scale: float = 1
    max_scale: float = 2.5
    scale_step_factor: float = 1.25
    microns_per_pixel: float = 1
    max_items_per_screen: float = 1.5
    points_closeness_factor: float = 10
    pan_strength_factor: float = 3
    current: ViewParams = field(default_factory=ViewParams)
    last: ViewParams = field(default_factory=ViewParams)
    mouse_move_timer: typing.Optional[QTimer] = None
    scheduled_pan: typing.Optional[QPoint] = None
    slide_helper: typing.Optional[SlideHelper] = None
    annotation_type: typing.Optional[AnnotationType] = None
    annotation_model: typing.Optional[AnnotationModel] = None
    annotation: typing.Optional[AnnotationGraphicsItem] = None
    annotation_is_in_progress: bool = False
    annotation_label_template: str = 'annotation_{}'
    slide_graphics_item: typing.Optional[SlideGraphicsItem] = None
    filter_graphics_item: typing.Optional[FilterGraphicsItem] = None
    slide_graphics_grid_item: typing.Optional[GridGraphicsItem] = None

    scaleChanged = pyqtSignal(float)
    minScaleChanged = pyqtSignal(float)

    gridVisibleChanged = pyqtSignal(bool)
    gridSizeChanged = pyqtSignal(tuple)
    filePathChanged = pyqtSignal(str)
    dropped = pyqtSignal()
    backgroundBrushChanged = pyqtSignal(QBrush)

    _annotationRemovedFromScene = pyqtSignal(str)

    def __post_init__(self, parent_: typing.Optional[QWidget]):
        super().__init__(parent_)
        self.id = None  # debug purpose
        scene = GraphicsScene(scale_provider=self, parent_=self)
        self.setScene(scene)
        # unlimited_rect = QRectF(-2 ** 31, -2 ** 31, 2 ** 32, 2 ** 32)
        # self.setSceneRect(unlimited_rect)
        self.setTransformationAnchor(QGraphicsView.NoAnchor)
        self.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        # self.setRenderHints(QPainter.Antialiasing | QPainter.SmoothPixmapTransform)
        self.scene().installEventFilter(self)
        # self.installEventFilter(self)
        self.scene().sceneRectChanged.connect(self.update_fit_and_min_scale)
        # self.scaleChanged.connect(self.on_scale_changed)
        self.setDisabled(True)
        # enables to switch between sub windows by mouse hover, but can slow down view browsing?
        # self.setMouseTracking(True)
        self.scene().addText(help_text)
        self.annotation_service.added_signal().connect(self.on_annotation_model_added)
        self.annotation_service.edited_signal().connect(self.on_annotation_model_edited)
        self.annotation_service.deleted_signal().connect(self.on_annotation_models_deleted)
        self._annotationRemovedFromScene.connect(self.__on_annotation_removed_from_scene)

        # self.scene().annotationModelsSelected.connect(self.on_scene_annotations_selected)

    def __on_annotation_removed_from_scene(self, id_: str):
        with slot_disconnected(self.annotation_service.deleted_signal(), self.on_annotation_models_deleted):
            self.annotation_service.delete([id_])

    def on_annotation_models_deleted(self, ids: typing.List[str]):
        with slot_disconnected(self._annotationRemovedFromScene, self.__on_annotation_removed_from_scene):
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
        # self.filter_graphics_item.update()
        self.filter_graphics_item.update()
        self.update()
        self.invalidateScene()

    def create_item_from_model(self, annotation_model: AnnotationModel):
        annotation = AnnotationGraphicsItem(id=annotation_model.id, scale_provider=self,
                                            model=build_annotation_graphics_model(annotation_model),
                                            is_in_progress=False,
                                            slide_stats_provider=self)

        # def __on_pos_changed(p: QPoint):
        #     print(f'__on_pos_changed: {self.id}')
        # annotation.update()
        # with slot_disconnected(self.annotation_service.edited_signal(), self.on_annotation_model_edited):
        # self.annotation_service.edit_origin_point(annotation_model.id, qpoint_to_ituple(p))

        def __on_removed_from_scene(id_: str):
            self._annotationRemovedFromScene.emit(id_)

        # annotation.signals.posChanged.connect(debounce_one_arg_slot(1 / 1000, __on_pos_changed))
        annotation.signals.posChanged.connect(self.on_pos_changed)
        annotation.signals.removedFromScene.connect(__on_removed_from_scene)
        return annotation

    @debounce_three_arg_slot_wrap(0.1)
    def on_pos_changed(self, id_: str, p: QPoint):
        # print(f'__on_pos_changed: {self.id}')
        # annotation.update()
        item = self.scene().annotations.get(id_)
        # item.update()
        # with slot_disconnected(self.annotation_service.edited_signal(), self.on_annotation_model_edited):
        self.annotation_service.edit_origin_point(id_, qpoint_to_ituple(p))

    def get_microns_per_pixel(self) -> float:
        return self.slide_helper.microns_per_pixel

    def get_scale(self):
        return self.get_current_view_scale()

    def get_background_brush(self) -> QBrush:
        return self.backgroundBrush()

    setBackgroundBrush = None

    def set_background_brush(self, brush: QBrush) -> None:
        QGraphicsView.setBackgroundBrush(self, brush)
        self.backgroundBrushChanged.emit(brush)

    def get_grid_visible(self) -> bool:
        return self.slide_graphics_grid_item is not None and self.slide_graphics_grid_item.isVisible()

    def set_grid_visible(self, visible: bool) -> None:
        # print(f'self: {id(self)}, sender: {id(self.sender())}')
        self.slide_graphics_grid_item.setVisible(visible)
        self.gridVisibleChanged.emit(visible)

    def get_grid_size(self) -> typing.Tuple[int, int]:
        return self.slide_graphics_grid_item.grid_size

    def set_grid_size(self, size: typing.Tuple[int, int]) -> None:
        self.slide_graphics_grid_item.grid_size = size
        self.slide_graphics_grid_item.update_lines()
        self.slide_graphics_grid_item.update()
        self.gridSizeChanged.emit(size)

    def get_file_path(self) -> str:
        return self.slide_helper.slide_path

    def set_file_path(self, file_path: str) -> None:
        self.slide_helper = SlideHelper(file_path)
        self.on_off_annotation()
        self.scene().clear()
        self.scene().setSceneRect(self.slide_helper.get_rect_for_level(0))
        unlimited_rect = QRectF(-2 ** 31, -2 ** 31, 2 ** 32, 2 ** 32)
        self.setSceneRect(unlimited_rect)
        self.scene().microns_per_pixel = self.slide_helper.microns_per_pixel
        # self.view.update_fit_and_min_scale()
        self.fit_scene()

        self.slide_graphics_item = SlideGraphicsItem(file_path)
        self.scene().addItem(self.slide_graphics_item)

        self.slide_graphics_grid_item = GridGraphicsItem(bounding_rect=self.slide_graphics_item.boundingRect(),
                                                         min_scale=self.min_scale, max_scale=self.max_scale)
        self.scene().addItem(self.slide_graphics_grid_item)

        self.filter_graphics_item = FilterGraphicsItem(self.pixmap_provider, self.slide_helper)
        self.scene().addItem(self.filter_graphics_item)

        self.filePathChanged.emit(file_path)

        # self.setDisabled(False)
        self.update()
        # self.adjustSize()

    def scene(self) -> GraphicsScene:
        return typing.cast(GraphicsScene, super().scene())

    def on_min_zoom_changed(self, new_min_zoom) -> None:
        if self.slide_graphics_grid_item:
            self.slide_graphics_grid_item.min_zoom = new_min_zoom

    # def on_scale_changed(self) -> None:
    #     for name, item in self.annotation_items.items():
    #         item.scale = self.get_current_view_scale()

    def viewportEvent(self, event: QEvent) -> bool:
        self.update_view_params(event, self.current)
        res = super().viewportEvent(event)
        self.update_view_params(event, self.last)
        if event.type() == QEvent.Resize:
            self.update_fit_and_min_scale()
        return res

    def update_view_params(self, event: QEvent, view_params: ViewParams) -> None:
        rect = self.viewport().rect()
        if isinstance(event, QResizeEvent):
            rect.setSize(event.oldSize())
            view_params.view_scene_center = self.mapToScene(self.mapFromGlobal(self.mapToGlobal(rect.center())))
        else:
            view_params.view_scene_center = self.mapToScene(rect.center())

        view_params.view_scene_top_left = self.mapToScene(rect.topLeft())
        if isinstance(event, QMouseEvent) or isinstance(event, QWheelEvent):
            view_params.mouse_pos = event.pos()
            view_params.mouse_scene_pos = self.mapToScene(event.pos())
            if event.type() == QEvent.MouseMove:
                view_params.mouse_move_between_press_and_release = True
            elif event.type() == QEvent.MouseButtonPress:
                view_params.mouse_move_between_press_and_release = False

    def update_fit_and_min_scale(self) -> None:
        vw, vh = self.width(), self.height()
        item_rect = self.scene().sceneRect()
        if item_rect and item_rect.width() and item_rect.height():
            iw, ih = item_rect.width(), item_rect.height()
            self.fit_scale = min(vw / iw, vh / ih)
            self.min_scale = self.fit_scale / self.max_items_per_screen
            # self.set_scale_in_view_center(self.get_current_view_scale())
            self.minScaleChanged.emit(self.min_scale)

    def get_scale_to_fit_rect(self, rect: QRectF) -> float:
        vw, vh = self.width(), self.height()
        if rect and rect.width() and rect.height():
            iw, ih = rect.width(), rect.height()
            fit_scale = min(vw / iw, vh / ih)
            return fit_scale
        else:
            return 1

    def wheelEvent(self, event: QtGui.QWheelEvent) -> None:
        steps_count = abs(event.angleDelta().y()) / 120
        is_scale_in = event.angleDelta().y() > 0
        scale_factor_ = self.scale_step_factor if is_scale_in else 1 / self.scale_step_factor
        scale_factor = scale_factor_ ** steps_count
        self.launch_scale_time_line(scale_factor)
        event.accept()

    def launch_scale_time_line(self, scale_factor: float) -> None:
        timeline = ScaleTimeLine(parent=self, scale_factor=scale_factor,
                                 value_changed_callback=self.on_scale_timeline_value_changed)
        timeline.start()

    def on_scale_timeline_value_changed(self, time_line_value: float, data: ScaleTimeLineData) -> None:
        current_scale = self.get_current_view_scale()
        time_line_value_delta = time_line_value - data.prev_time_line_value
        new_scale = current_scale * data.scale_factor ** time_line_value_delta
        current_mouse_pos = self.mapFromGlobal(QCursor().pos())
        # self.set_scale_in_mouse_point(new_scale, self.current.mouse_pos)
        self.set_scale_in_mouse_point(new_scale, current_mouse_pos)
        data.prev_time_line_value = time_line_value
        self.current.view_scene_top_left = self.mapToScene(self.viewport().rect().topLeft())
        self.last.view_scene_top_left = self.mapToScene(self.viewport().rect().topLeft())

    def fit_scene(self) -> None:
        self.fit_rect(self.scene().sceneRect())

    def fit_rect(self, rect: QRectF) -> None:
        fit_scale = self.get_scale_to_fit_rect(rect)
        self.set_scale_in_scene_point(fit_scale, rect.center())

    def set_scale_in_mouse_point(self, new_scale: float, mouse_view_pos: QPoint) -> None:
        m, top_left_old = self.mapToScene(mouse_view_pos), self.mapToScene(self.rect().topLeft())
        old_scale = self.get_current_view_scale()
        new_scale = self.limit_new_scale(new_scale)

        top_left_new = m - (m - top_left_old) * old_scale / new_scale
        self.resetTransform()
        # print(f"top_left: {top_left_new}")
        transform = QTransform().scale(new_scale, new_scale).translate(-top_left_new.x(), -top_left_new.y())
        self.setTransform(transform)
        # self.scaleChanged.emit(self.get_current_view_scale())

    def set_scale_in_view_center(self, new_scale: float) -> None:
        new_scale = self.limit_new_scale(new_scale)
        # view_scene_center = self.mapToScene(self.viewport().rect().center())
        view_scene_center = self.mapToScene(self.rect().center())
        self.resetTransform()
        # print(f'view_scene_rect: {view_scene_center}, new: {self.mapToScene(self.rect().center())}')
        # transform=QTransform().scale(new_scale, new_scale)
        # shift= view_scene_center - transform.map(self.rect().bottomRight()) / 2
        # transform.translate(shift.x(),shift.y())
        # self.setTransform(transform)

        self.scale(new_scale, new_scale)
        shift = view_scene_center - self.mapToScene(self.rect().bottomRight()) / 2
        self.translate(-shift.x(), -shift.y())

    def set_scale_in_scene_point(self, new_scale: float, scene_point: QPointF) -> None:
        new_scale = self.limit_new_scale(new_scale)
        self.resetTransform()
        self.scale(new_scale, new_scale)
        shift = scene_point - self.mapToScene(self.rect().bottomRight()) / 2
        self.translate(-shift.x(), -shift.y())

    def limit_new_scale(self, new_scale: float) -> float:
        if new_scale > self.max_scale:
            new_scale = self.max_scale
        elif new_scale < self.min_scale:
            new_scale = self.min_scale
        return new_scale

    def get_current_view_scale(self) -> float:
        return self.transform().m11()

    def mouseMoveEvent(self, event: QtGui.QMouseEvent) -> None:
        if int(event.buttons()) & Qt.LeftButton == Qt.LeftButton and not self.scene().mouseGrabberItem():
            self.scheduled_pan = (self.current.mouse_pos - self.last.mouse_pos) / self.get_current_view_scale()
            self.mouse_move_timer = AlmostImmediateTimer(self, self.__on_almost_immediate_move)
            self.mouse_move_timer.start()
            event.accept()
        elif self.annotation_type and self.annotation_is_in_progress:
            point_scene = self.current.mouse_scene_pos.toPoint()
            # first_point = ituple_to_qpoint(self.annotation_model.geometry.points[0])
            first_point = ituple_to_qpoint(self.annotation_service.get_first_point(self.annotation.id))
            if self.annotation_type == AnnotationType.POLYGON and self.are_points_close(
                    point_scene, first_point):
                point_scene = first_point
            # self.annotation_model.geometry.points[-1] = qpoint_to_ituple(point_scene)
            # print("mouseMove before edit_last_point")
            self.annotation_service.edit_last_point(self.annotation.id, qpoint_to_ituple(point_scene))
            # print("mouseMove after edit_last_point")
            # self.scene().edit_annotation(self.annotation_model)
            self.annotation.update()
            event.accept()
        else:
            super().mouseMoveEvent(event)

    def __on_almost_immediate_move(self) -> None:
        self.translate(self.scheduled_pan.x(), self.scheduled_pan.y())

    def mouseReleaseEvent(self, event: QMouseEvent) -> None:
        if event.button() == Qt.LeftButton and self.mouse_move_timer and self.mouse_move_timer.isActive() and not self.scene().mouseGrabberItem():
            # print("release")
            self.mouse_move_timer.stop()
            self.launch_pan_time_line(self.scheduled_pan * self.pan_strength_factor)
            event.accept()
            return
        if not self.current.mouse_move_between_press_and_release:
            res = self.on_mouse_click(event)
            if res:
                event.accept()
                return
        super().mouseReleaseEvent(event)

    def on_mouse_click(self, event: QMouseEvent) -> bool:
        if event.button() == Qt.LeftButton:
            if not self.annotation_type:
                return False
            else:
                if self.annotation_is_in_progress:
                    self.__annotation_progress_click()
                else:
                    self.on_start_annotation()
                return True
        return False

    def __annotation_progress_click(self):
        if self.annotation_type == AnnotationType.POLYGON:
            annotation_model = self.annotation_service.get(self.annotation.id)
            if self.are_points_close(self.current.mouse_scene_pos.toPoint(),
                                     ituple_to_qpoint(annotation_model.geometry.points[0])):
                self.__on_finish_annotation()
            else:
                self.annotation_service.add_point(self.annotation.id,
                                                  qpoint_to_ituple(self.current.mouse_scene_pos.toPoint()))
            # if self.are_points_close(self.current.mouse_scene_pos.toPoint(),
            #                          ituple_to_qpoint(self.annotation_model.geometry.points[0])):
            #     self.__on_finish_annotation()
            # else:
            #     self.annotation_model.geometry.points.append(qpoint_to_ituple(self.current.mouse_scene_pos.toPoint()))
            #     self.scene().edit_annotation(self.annotation_model)
        else:
            self.__on_finish_annotation()

    def on_start_annotation(self) -> None:
        if self.annotation:
            self.scene().removeItem(self.annotation)
        start_point = qpoint_to_ituple(self.current.mouse_scene_pos.toPoint())
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
        self.setMouseTracking(True)
        self.annotation_is_in_progress = True
        self.annotation.update()

    def __on_finish_annotation(self) -> None:
        annotation_model = self.annotation_service.get(self.annotation.id)
        if not annotation_model.geometry.is_distinguishable_from_point():
            self.scene().remove_annotations([self.annotation.id])
            # self.scene().removeItem(self.annotation)

        self.annotation.is_in_progress = False
        self.annotation.update()
        self.annotation = None
        self.on_off_annotation()

    def on_off_annotation(self) -> None:
        self.annotation_is_in_progress = False
        self.setMouseTracking(False)
        if self.annotation:
            id = self.annotation.id
            self.annotation = None
            # self.annotation_model = None
            self.scene().remove_annotations([id])
            # self.scene().removeItem(self.annotation)

    def are_points_close(self, p1: QPoint, p2: QPoint) -> bool:
        length = QVector2D(p1 - p2).length()
        return length < self.points_closeness_factor / self.get_current_view_scale()

    def eventFilter(self, source: QObject, event: QEvent) -> bool:
        if isinstance(event, QGraphicsSceneDragDropEvent):
            drag_events = [QEvent.GraphicsSceneDragEnter, QEvent.GraphicsSceneDragMove]
            drop_events = [QEvent.GraphicsSceneDrop]
            if event.type() in drag_events and mime_data_is_url(event.mimeData()):
                event.accept()
                return True
            elif event.type() in drop_events and mime_data_is_url(event.mimeData()):
                file_path = event.mimeData().urls()[0].toLocalFile()
                # print(file_path)
                self.set_file_path(file_path)
                event.accept()
                self.dropped.emit()
                return True
        elif KeyPressEventUtil.is_enter(event):
            self.on_enter_press()
            return True
        elif KeyPressEventUtil.is_esc(event):
            self.on_esc_press()
            return True
        elif KeyPressEventUtil.is_delete(event):
            self.on_delete_press()
            return True
        else:
            return super().eventFilter(source, event)

    def on_enter_press(self) -> None:
        if self.annotation_is_in_progress:
            if self.annotation_type == AnnotationType.POLYGON:
                first_point = self.annotation_service.get_first_point(self.annotation.id)
                self.annotation_service.edit_last_point(self.annotation.id, first_point)
            self.__on_finish_annotation()

    def on_esc_press(self):
        if self.annotation_is_in_progress:
            self.on_off_annotation()

    def on_delete_press(self):
        if self.annotation_is_in_progress:
            self.on_off_annotation()
        else:
            annotations_to_remove = [i for i in self.scene().annotations.values() if i.isSelected()]
            for annotation in annotations_to_remove:
                self.scene().removeItem(annotation)

    def launch_pan_time_line(self, pan: QPoint) -> None:
        timeline = PanTimeLine(parent=self, pan=pan,
                               value_changed_callback=self.__on_pan_timeline_value_changed)
        timeline.start()

    def __on_pan_timeline_value_changed(self, time_line_value: float, data: PanTimeLineData) -> None:
        time_line_value_delta = time_line_value - data.prev_time_line_value
        translate_point = data.pan * time_line_value_delta
        self.translate(translate_point.x(), translate_point.y())
        # self.current.mouse_pos = self.last.mouse_pos + data.pan * time_line_value_delta
        data.prev_time_line_value = time_line_value

    def log_state(self) -> None:
        print("scene_rect: {} view_scene_rect: {} scale: {}".format(self.scene().sceneRect(), self.sceneRect(),
                                                                    self.get_current_view_scale()))

    @debug_only()
    def init_debug_scene_view_rect(self) -> None:
        self.filePathChanged.connect(lambda: self.scene().addItem(SlideGraphicsDebugViewSceneRect(self.view)))

    @debug_only()
    def init_debug_item_rect(self) -> None:
        self.filePathChanged.connect(
            lambda: self.scene().addItem(SlideGraphicsDebugItemRect(self.slide_graphics_item)))
