import copy
import typing

from PyQt5 import QtGui
from PyQt5.QtCore import QMutex, QObject, Qt, QPointF, pyqtSignal, QEvent, QPoint, QRectF
from PyQt5.QtGui import QTransform, QVector2D, QMouseEvent, QWheelEvent, QResizeEvent
from PyQt5.QtWidgets import QGraphicsView, QGraphicsScene, QWidget, QGraphicsItemGroup

from slide_viewer.ui.dict_tree_view_model.config import default_instance_odict, Sequence
from slide_viewer.ui.dict_tree_view_model.standard_attr_key import StandardAttrKey
from slide_viewer.ui.slide.graphics.annotation.annotation_data import AnnotationData
from slide_viewer.ui.common.almost_immediate_timer import AlmostImmediateTimer
from slide_viewer.ui.common.common import is_key_press_event
from slide_viewer.ui.slide.graphics.annotation.annotation_path_item import AnnotationPathItem
from slide_viewer.ui.slide.graphics.annotation.annotation_type import AnnotationType
from slide_viewer.ui.slide.graphics.slide_viewer_pan_time_line import SlideViewerPanTimeLine, PanTimeLineData
from slide_viewer.ui.slide.graphics.slide_viewer_scale_time_line import ScaleTimeLineData, SlideViewerScaleTimeLine

view_mutex = QMutex()
scale_step_factor = 1.25


class ViewParams:
    def __init__(self):
        self.mouse_scene_pos: QPointF = None
        self.view_scene_top_left: QPointF = None
        self.view_scene_center: QPointF = None
        self.mouse_pos: QPoint = None
        self.mouse_move_between_press_and_release: bool = False


class SlideViewerGraphicsView(QGraphicsView):
    scaleChanged = pyqtSignal(float)
    minScaleChanged = pyqtSignal(float)
    annotationItemAdded = pyqtSignal(QGraphicsItemGroup)
    annotationItemsSelected = pyqtSignal(list)
    annotationItemRemoved = pyqtSignal(int)

    def __init__(self, scene: QGraphicsScene, odict_factory, parent: typing.Optional[QWidget] = None):
        super().__init__(scene, parent)
        self.setTransformationAnchor(QGraphicsView.NoAnchor)
        self.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        # self.setRenderHints(QPainter.Antialiasing | QPainter.SmoothPixmapTransform)
        self.current, self.last = ViewParams(), ViewParams()
        self.mouse_move_timer = None
        self.fit_scale, self.min_scale, self.max_scale = 1, 1, 2.5
        self.scheduled_pan: QPoint = None

        self.annotation_type: AnnotationType = None
        self.annotation_item = None
        self.annotation_items: typing.List[AnnotationPathItem] = []
        self.annotation_item_in_progress = False

        self.microns_per_pixel = 1
        self.installEventFilter(self)

        self.odict_factory = odict_factory

        self.scene().selectionChanged.connect(self.on_selection_changed)
        self.scene().sceneRectChanged.connect(self.update_fit_and_min_scale)

        self.scaleChanged.connect(self.on_scale_changed)

    def on_scale_changed(self):
        for item in self.annotation_items:
            item.scale = self.get_current_view_scale()

    def on_selection_changed(self):
        selected_items = set(self.scene().selectedItems())
        item_numbers = []
        for i, annotation_item in enumerate(self.annotation_items):
            if annotation_item in selected_items:
                item_numbers.append(i)
        # print(f"SlideViewerGraphicsView.on_selection_changed selected_items: {selected_items}, item_numbers: {item_numbers}")
        self.annotationItemsSelected.emit(item_numbers)

    def reset(self):
        self.resetTransform()
        self.horizontalScrollBar().setValue(0)
        self.verticalScrollBar().setValue(0)
        self.scaleChanged.emit(self.get_current_view_scale())

    def fit_scene(self):
        self.fit_rect(self.scene().sceneRect())

    def fit_rect(self, rect: QRectF):
        self.reset()
        fit_scale = self.get_scale_to_fit_rect(rect)
        self.scale(fit_scale, fit_scale)
        self.centerOn(rect.center())
        self.scaleChanged.emit(self.get_current_view_scale())

    def viewportEvent(self, event: QEvent) -> bool:
        self.update_view_params(event, self.current)
        res = super().viewportEvent(event)
        self.update_view_params(event, self.last)
        if event.type() == QEvent.Resize:
            self.update_fit_and_min_scale()
        return res

    def update_view_params(self, event: QEvent, view_params: ViewParams):
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

    def update_fit_and_min_scale(self):
        vw, vh = self.width(), self.height()
        item_rect = self.scene().sceneRect()
        if item_rect and item_rect.width() and item_rect.height():
            iw, ih = item_rect.width(), item_rect.height()
            max_items_per_screen = 1.5
            self.fit_scale = min(vw / iw, vh / ih)
            self.min_scale = self.fit_scale / max_items_per_screen
            self.set_scale_in_view_center(self.get_current_view_scale())
            self.minScaleChanged.emit(self.min_scale)

    def get_scale_to_fit_rect(self, rect: QRectF):
        vw, vh = self.width(), self.height()
        if rect and rect.width() and rect.height():
            iw, ih = rect.width(), rect.height()
            fit_scale = min(vw / iw, vh / ih)
            return fit_scale

    def wheelEvent(self, event: QtGui.QWheelEvent) -> None:
        steps_count = abs(event.angleDelta().y()) / 120
        is_scale_in = event.angleDelta().y() > 0
        scale_factor_ = scale_step_factor if is_scale_in else 1 / scale_step_factor
        scale_factor = scale_factor_ ** steps_count
        self.launch_scale_time_line(scale_factor)
        event.accept()

    def launch_scale_time_line(self, scale_factor: float):
        timeline = SlideViewerScaleTimeLine(self, scale_factor, self.on_scale_timeline_value_changed)
        timeline.start()

    def on_scale_timeline_value_changed(self, time_line_value: float, data: ScaleTimeLineData):
        current_scale = self.get_current_view_scale()
        time_line_value_delta = time_line_value - data.prev_time_line_value
        new_scale = current_scale * data.scale_factor ** time_line_value_delta
        self.set_scale_in_mouse_point(new_scale)
        data.prev_time_line_value = time_line_value
        self.current.view_scene_top_left = self.mapToScene(self.viewport().rect().topLeft())
        self.last.view_scene_top_left = self.mapToScene(self.viewport().rect().topLeft())

    def set_scale_in_mouse_point(self, new_scale: float):
        m, top_left_old = self.current.mouse_scene_pos, self.current.view_scene_top_left
        old_scale = self.get_current_view_scale()
        new_scale = self.limit_new_scale(new_scale)

        top_left_new = m - (m - top_left_old) * old_scale / new_scale
        self.reset()
        # print("top_left", top_left_new.x())
        transform = QTransform().scale(new_scale, new_scale).translate(-top_left_new.x(), -top_left_new.y())
        self.setTransform(transform, False)
        self.scaleChanged.emit(self.get_current_view_scale())

    def set_scale_in_view_center(self, new_scale: float):
        new_scale = self.limit_new_scale(new_scale)
        # view_scene_center = self.mapToScene(self.viewport().rect().center())
        view_scene_center = self.mapToScene(self.rect().center())
        self.reset()
        self.scale(new_scale, new_scale)
        self.centerOn(view_scene_center)
        self.scaleChanged.emit(self.get_current_view_scale())

    def limit_new_scale(self, new_scale: float):
        if new_scale > self.max_scale:
            new_scale = self.max_scale
        elif new_scale < self.min_scale:
            new_scale = self.min_scale
        return new_scale

    def get_current_view_scale(self):
        return self.transform().m11()

    def mouseMoveEvent(self, event: QtGui.QMouseEvent) -> None:
        if event.buttons() & Qt.LeftButton == Qt.LeftButton and not self.scene().mouseGrabberItem():
            self.scheduled_pan = (self.current.mouse_pos - self.last.mouse_pos) / self.get_current_view_scale()
            self.mouse_move_timer = AlmostImmediateTimer(self, self.on_almost_immediate_move)
            self.mouse_move_timer.start()
            event.accept()
        elif self.annotation_type and self.annotation_item_in_progress:
            point_scene = self.current.mouse_scene_pos
            if self.annotation_type == AnnotationType.POLYGON and self.are_points_close(
                    point_scene, self.annotation_item.first_point()):
                point_scene = self.annotation_item.first_point()
            self.annotation_item.set_last_point(point_scene)
            event.accept()
        else:
            super().mouseMoveEvent(event)

    def on_almost_immediate_move(self):
        self.translate(self.scheduled_pan.x(), self.scheduled_pan.y())

    def mouseReleaseEvent(self, event: QMouseEvent) -> None:
        if event.button() == Qt.LeftButton and self.mouse_move_timer and self.mouse_move_timer.isActive() and not self.scene().mouseGrabberItem():
            # print("release")
            self.mouse_move_timer.stop()
            self.launch_pan_time_line(self.scheduled_pan * 3)
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
                if self.annotation_item_in_progress:
                    if self.annotation_type == AnnotationType.POLYGON:
                        if self.are_points_close(self.current.mouse_scene_pos,
                                                 self.annotation_item.first_point()):
                            self.on_finish_annotation_item()
                        else:
                            self.annotation_item.add_point(self.current.mouse_scene_pos)
                    else:
                        self.on_finish_annotation_item()
                else:
                    self.on_start_annotation_item()
                return True
        return False

    def on_start_annotation_item(self):
        if self.annotation_item:
            self.scene().removeItem(self.annotation_item)
        # template_odict = self.annotation_item_odict_template
        odict = self.odict_factory()
        odict[StandardAttrKey.name.name] = f"annotation{Sequence.next_number()}"
        odict[StandardAttrKey.annotation_type.name] = self.annotation_type
        odict[StandardAttrKey.points.name] = []
        annotation_data = AnnotationData(odict)
        # self.annotation_item = create_annotation_item(self.annotation_type, self.microns_per_pixel)
        self.annotation_item = AnnotationPathItem(annotation_data, self.microns_per_pixel,
                                                  self.get_current_view_scale())
        self.annotation_item.is_in_progress = True
        self.scene().addItem(self.annotation_item)
        self.annotation_item.setVisible(True)
        self.annotation_item.add_point(self.current.mouse_scene_pos)
        self.annotation_item.add_point(self.current.mouse_scene_pos)
        # self.annotation_item.set_points([self.current.mouse_scene_pos, self.current.mouse_scene_pos])
        self.setMouseTracking(True)
        self.annotation_item_in_progress = True

    def on_finish_annotation_item(self):
        if self.annotation_item and self.annotation_item.shape_item.path().length():
            self.annotation_items.append(self.annotation_item)
            self.annotation_item.is_in_progress = False
            self.annotation_item.update()
            self.annotationItemAdded.emit(self.annotation_item)
        self.on_off_annotation_item()

    def on_off_annotation_item(self):
        self.annotation_item_in_progress = False
        self.setMouseTracking(False)
        self.annotation_item = None

    def reset_annotation_items(self, odicts: list = []):
        for item in self.annotation_items:
            if item and item.scene():
                item.scene().removeItem(item)
        self.annotation_items = []
        for odict in odicts:
            adata = AnnotationData(odict)
            item = AnnotationPathItem(adata, self.microns_per_pixel, self.get_current_view_scale())
            item.setVisible(True)
            self.annotation_items.append(item)
            self.scene().addItem(item)

    # def remove_annotation_item(self, item_number):
    #     item = self.annotation_items[item_number]
    #     if item and item.scene():
    #         item.scene().removeItem(item)
    #     del self.annotation_items[item_number]
    #     self.annotationItemsRemoved.emit(item_number)

    def are_points_close(self, p1: QPointF, p2: QPointF):
        length = QVector2D(p1 - p2).length()
        # print(length)
        return length < 10 / self.get_current_view_scale()

    def eventFilter(self, source: QObject, event: QEvent) -> bool:
        if is_key_press_event(event):
            self.on_enter_press()
            return True
        else:
            return super().eventFilter(source, event)

    def on_enter_press(self):
        if self.annotation_item_in_progress and self.annotation_type == AnnotationType.POLYGON:
            self.annotation_item.set_last_point(self.annotation_item.first_point())
            self.on_finish_annotation_item()

    def launch_pan_time_line(self, pan: QPoint):
        timeline = SlideViewerPanTimeLine(self, pan, self.on_pan_timeline_value_changed)
        timeline.start()

    def on_pan_timeline_value_changed(self, time_line_value: float, data: PanTimeLineData):
        time_line_value_delta = time_line_value - data.prev_time_line_value
        translate_point = data.pan * time_line_value_delta
        self.translate(translate_point.x(), translate_point.y())
        self.current.mouse_pos = self.last.mouse_pos + data.pan * time_line_value_delta
        data.prev_time_line_value = time_line_value


def log_state(self):
    print("scene_rect: {} view_scene_rect: {} scale: {}".format(self.scene().sceneRect(), self.sceneRect(),
                                                                self.get_current_view_scale()))
