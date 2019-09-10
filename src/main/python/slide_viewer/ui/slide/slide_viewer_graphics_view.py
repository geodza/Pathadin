import typing

from PyQt5 import QtGui
from PyQt5.QtCore import QTimeLine, QMutex, QObject, Qt, QTimer, QPointF, pyqtSignal, QEvent
from PyQt5.QtGui import QTransform, QVector2D, QMouseEvent, QWheelEvent, QResizeEvent, QKeyEvent, QPainterPath
from PyQt5.QtWidgets import QGraphicsView, QGraphicsScene, QWidget, QGraphicsItemGroup, QGraphicsItem

from slide_viewer.ui.annotation.annotation_data import AnnotationData
from slide_viewer.ui.annotation.annotation_path_item import AnnotationPathItem
from slide_viewer.ui.annotation.annotation_type import AnnotationType
from slide_viewer.ui.annotation.annotation_item_factory import create_annotation_item

view_mutex = QMutex()
scale_step_factor = 1.25


class ScaleTimeLineData:
    def __init__(self, scale_factor):
        self.scale_factor = scale_factor
        self.prev_time_line_value = 0


class PanTimeLineData:
    def __init__(self, pan):
        self.pan = pan
        self.prev_time_line_value = 0


class ViewParams:
    def __init__(self):
        self.mouse_scene_pos = None
        self.view_scene_top_left = None
        self.view_scene_center = None
        self.mouse_pos = None


class SlideViewerGraphicsView(QGraphicsView):
    scaleChanged = pyqtSignal(float)
    minScaleChanged = pyqtSignal(float)
    annotationItemAdded = pyqtSignal(QGraphicsItemGroup)
    annotationItemsSelected = pyqtSignal(list)
    annotationItemRemoved = pyqtSignal(int)

    def __init__(self, scene: QGraphicsScene, parent: typing.Optional[QWidget] = ...):
        super().__init__(scene, parent)
        self.setTransformationAnchor(QGraphicsView.NoAnchor)
        self.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        # self.setRenderHints(QPainter.Antialiasing | QPainter.SmoothPixmapTransform)
        self.current = ViewParams()
        self.last = ViewParams()
        self.mouse_move_timer = None
        self.fit_scale = 1
        self.min_scale = 1
        self.max_scale = 2.5
        self.pan = None
        self.move_mode = "straighten"
        self.mouse_move_between_press_and_release = False

        self.annotation_type: AnnotationType = None
        self.annotation_item = None
        self.annotation_items = []
        self.annotation_item_in_progress = False

        self.microns_per_pixel = 1

        self.installEventFilter(self)

    def reset(self):
        self.resetTransform()
        self.horizontalScrollBar().setValue(0)
        self.verticalScrollBar().setValue(0)
        self.scaleChanged.emit(self.get_current_view_scale())

    def fit_scene(self):
        self.reset()
        # self.update_view_scene_rect_and_min_scale()
        self.scale(self.fit_scale, self.fit_scale)
        self.centerOn(self.scene().sceneRect().center())
        self.scaleChanged.emit(self.get_current_view_scale())

    def viewportEvent(self, event: QEvent) -> bool:
        self.update_view_params(event, self.current)
        res = super().viewportEvent(event)
        self.update_view_params(event, self.last)
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

    def update_fit_and_min_scale(self):
        vw, vh = self.width(), self.height()
        item_rect = self.scene().sceneRect()
        if item_rect:
            iw, ih = item_rect.width(), item_rect.height()
            max_items_per_screen = 1.5
            self.fit_scale = min(vw / iw, vh / ih)
            self.min_scale = self.fit_scale / max_items_per_screen
            self.minScaleChanged.emit(self.min_scale)

    def wheelEvent(self, event: QtGui.QWheelEvent) -> None:
        steps_count = abs(event.angleDelta().y()) / 120
        is_scale_in = event.angleDelta().y() > 0
        scale_factor_ = scale_step_factor if is_scale_in else 1 / scale_step_factor
        scale_factor = scale_factor_ ** steps_count
        self.launch_scale_time_line(scale_factor)
        event.accept()

    def launch_scale_time_line(self, scale_factor):
        timeline = QTimeLine(250, self)
        timeline.setUpdateInterval(15)
        timeline.setProperty("scale_time_line_data", ScaleTimeLineData(scale_factor))
        timeline.valueChanged.connect(self.on_scale_timeline_value_changed)
        timeline.start()

    def on_scale_timeline_value_changed(self, time_line_value):
        scale_time_line_data: ScaleTimeLineData = self.sender().property("scale_time_line_data")
        current_scale = self.get_current_view_scale()
        time_line_value_delta = time_line_value - scale_time_line_data.prev_time_line_value
        new_scale = current_scale * scale_time_line_data.scale_factor ** time_line_value_delta
        self.set_scale_in_mouse_point(new_scale)
        scale_time_line_data.prev_time_line_value = time_line_value
        self.current.view_scene_top_left = self.mapToScene(self.viewport().rect().topLeft())
        self.last.view_scene_top_left = self.mapToScene(self.viewport().rect().topLeft())

    def set_scale_in_mouse_point(self, new_scale):
        m, top_left_old = self.current.mouse_scene_pos, self.current.view_scene_top_left
        old_scale = self.get_current_view_scale()
        new_scale = self.limit_new_scale(new_scale)

        top_left_new = m - (m - top_left_old) * old_scale / new_scale
        self.reset()
        # print("top_left", top_left_new.x())
        transform = QTransform().scale(new_scale, new_scale).translate(-top_left_new.x(), -top_left_new.y())
        self.setTransform(transform, False)
        self.scaleChanged.emit(self.get_current_view_scale())

    def set_scale_in_view_center(self, new_scale):
        new_scale = self.limit_new_scale(new_scale)
        # view_scene_center = self.mapToScene(self.viewport().rect().center())
        view_scene_center = self.mapToScene(self.rect().center())
        self.reset()
        self.scale(new_scale, new_scale)
        self.centerOn(view_scene_center)
        self.scaleChanged.emit(self.get_current_view_scale())

    def limit_new_scale(self, new_scale):
        if new_scale > self.max_scale:
            new_scale = self.max_scale
        elif new_scale < self.min_scale:
            new_scale = self.min_scale
        return new_scale

    def get_current_view_scale(self):
        scale = self.transform().m11()
        return scale

    def mousePressEvent(self, event: QtGui.QMouseEvent) -> None:
        self.mouse_move_between_press_and_release = False
        super().mousePressEvent(event)

    def mouseMoveEvent(self, event: QtGui.QMouseEvent) -> None:
        self.mouse_move_between_press_and_release = True
        if event.buttons() & Qt.LeftButton == Qt.LeftButton and not self.scene().mouseGrabberItem():
            self.pan = (self.current.mouse_pos - self.last.mouse_pos) / self.get_current_view_scale()
            self.mouse_move_timer = QTimer(self)
            self.mouse_move_timer.setInterval(0)
            self.mouse_move_timer.timeout.connect(self.on_almost_immediate_move)
            self.mouse_move_timer.setSingleShot(True)
            self.mouse_move_timer.start()
            event.accept()
            return
        elif self.annotation_type and self.annotation_item_in_progress:
            point_scene = self.current.mouse_scene_pos
            if self.annotation_type == AnnotationType.POLYGON and self.are_points_close(
                    point_scene, self.annotation_item.first_point()):
                point_scene = self.annotation_item.first_point()
            self.annotation_item.set_last_point(point_scene)
            event.accept()
            return
        super().mouseMoveEvent(event)

    def on_almost_immediate_move(self):
        self.translate(self.pan.x(), self.pan.y())

    def mouseReleaseEvent(self, event: QMouseEvent) -> None:
        if event.button() == Qt.LeftButton and self.mouse_move_timer and self.mouse_move_timer.isActive() and not self.scene().mouseGrabberItem():
            # print("release")
            self.mouse_move_timer.stop()
            self.launch_pan_time_line(self.pan * 3)
            event.accept()
            return
        if not self.mouse_move_between_press_and_release:
            if self.on_mouse_click(event):
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
        self.annotation_item = create_annotation_item(self.annotation_type, self.microns_per_pixel)
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
            self.annotationItemAdded.emit(self.annotation_item)
        self.on_off_annotation_item()

    def on_off_annotation_item(self):
        self.annotation_item_in_progress = False
        self.setMouseTracking(False)
        self.annotation_item = None

    def reset_annotation_items(self, annotation_data: typing.List[AnnotationData] = []):
        for item in self.annotation_items:
            if item and item.scene():
                item.scene().removeItem(item)
        self.annotation_items = []
        for annotation_datum in annotation_data:
            item = AnnotationPathItem(annotation_datum)
            item.setVisible(True)
            self.annotation_items.append(item)
            self.scene().addItem(item)
        # self.update()
        # self.scene().update()

    # def remove_annotation_item(self, item_number):
    #     item = self.annotation_items[item_number]
    #     if item and item.scene():
    #         item.scene().removeItem(item)
    #     del self.annotation_items[item_number]
    #     self.annotationItemsRemoved.emit(item_number)

    def on_select(self):
        size = 10 / self.get_current_view_scale()
        path = QPainterPath()
        path.addEllipse(self.current.mouse_scene_pos, size, size)
        self.scene().setSelectionArea(path, 0, Qt.IntersectsItemShape, self.viewportTransform())
        # print("select_path", path.boundingRect().toRect())
        # print(self.scene().selectedItems())
        item_numbers = [self.annotation_items.index(item) for item in self.scene().selectedItems()]
        self.annotationItemsSelected.emit(item_numbers)

    def are_points_close(self, p1: QPointF, p2: QPointF):
        length = QVector2D(p1 - p2).length()
        # print(length)
        return length < 10 / self.get_current_view_scale()

    def eventFilter(self, source: QObject, event: QEvent) -> bool:
        if event.type() == QEvent.KeyPress:
            key_event: QKeyEvent = event
            if key_event.key() == Qt.Key_Enter or key_event.key() == Qt.Key_Return:
                self.on_enter_press()
                return True

        return super().eventFilter(source, event)

    def on_enter_press(self):
        if self.annotation_item_in_progress and self.annotation_type == AnnotationType.POLYGON:
            self.annotation_item.set_last_point(self.annotation_item.first_point())
            self.on_finish_annotation_item()

    def launch_pan_time_line(self, pan):
        pan_timeline = QTimeLine(400, self)
        pan_timeline.setUpdateInterval(15)
        pan_timeline.setProperty("pan_time_line_data", PanTimeLineData(pan))
        pan_timeline.valueChanged.connect(self.on_pan_timeline_value_changed)
        pan_timeline.start()

    def on_pan_timeline_value_changed(self, time_line_value):
        pan_time_line_data: PanTimeLineData = self.sender().property("pan_time_line_data")
        time_line_value_delta = time_line_value - pan_time_line_data.prev_time_line_value
        translate_point = pan_time_line_data.pan * time_line_value_delta
        self.translate(translate_point.x(), translate_point.y())
        # self.last_mouse_pos = new_point
        self.current.mouse_pos = self.last.mouse_pos + pan_time_line_data.pan * time_line_value_delta
        pan_time_line_data.prev_time_line_value = time_line_value

    def log_state(self):
        print("scene_rect: {} view_scene_rect: {} scale: {}".format(self.scene().sceneRect(), self.sceneRect(),
                                                                    self.get_current_view_scale()))
