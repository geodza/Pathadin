import time
import typing
from PyQt5 import QtGui, QtCore
from PyQt5.QtCore import QTimeLine, QMutex, QMutexLocker, QObject, Qt, QTimer, QPoint, QPointF, QRect, QRectF, \
    pyqtSignal, QEvent
from PyQt5.QtGui import QTransform, QVector2D, QPainter, QMouseEvent, QWheelEvent, QResizeEvent
from PyQt5.QtWidgets import QGraphicsView, QGraphicsScene, QWidget

view_mutex = QMutex()
zoom_step_factor = 1.25


class ZoomTimeLineData:
    def __init__(self, zoom_factor):
        self.zoom_factor = zoom_factor
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
    zoomChanged = pyqtSignal(float)
    minZoomChanged = pyqtSignal(float)
    fitZoomChanged = pyqtSignal(float)

    def __init__(self, scene: QGraphicsScene, parent: typing.Optional[QWidget] = ...):
        super().__init__(scene, parent)
        self.setTransformationAnchor(QGraphicsView.NoAnchor)
        self.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        # self.setRenderHints(QPainter.Antialiasing | QPainter.SmoothPixmapTransform)
        self.current = ViewParams()
        self.last = ViewParams()
        self.mouse_move_timer = None
        self.fit_zoom = 1
        self.min_zoom = 1
        self.max_zoom = 2.5
        self.pan = None

    def reset(self):
        self.resetTransform()
        self.horizontalScrollBar().setValue(0)
        self.verticalScrollBar().setValue(0)
        self.zoomChanged.emit(self.get_current_view_scale())

    def fit_scene(self):
        self.reset()
        # self.update_view_scene_rect_and_min_zoom()
        self.scale(self.fit_zoom, self.fit_zoom)
        self.centerOn(self.scene().sceneRect().center())
        self.zoomChanged.emit(self.get_current_view_scale())

    def viewportEvent(self, event: QEvent) -> bool:
        self.update_view_params(event, self.current)
        res = super().viewportEvent(event)
        self.update_view_params(event, self.last)
        self.update_fit_and_min_zoom()
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

    def update_fit_and_min_zoom(self):
        vw, vh = self.width(), self.height()
        item_rect = self.scene().sceneRect()
        if item_rect:
            iw, ih = item_rect.width(), item_rect.height()
            max_items_per_screen = 1.5
            self.fit_zoom = min(vw / iw, vh / ih)
            self.min_zoom = self.fit_zoom / max_items_per_screen
            self.fitZoomChanged.emit(self.fit_zoom)
            self.minZoomChanged.emit(self.min_zoom)

    def wheelEvent(self, event: QtGui.QWheelEvent) -> None:
        steps_count = abs(event.angleDelta().y()) / 120
        is_zoom_in = event.angleDelta().y() > 0
        zoom_factor_ = zoom_step_factor if is_zoom_in else 1 / zoom_step_factor
        zoom_factor = zoom_factor_ ** steps_count
        self.launch_zoom_time_line(zoom_factor)
        event.accept()

    def launch_zoom_time_line(self, zoom_factor):
        zoom_timeline = QTimeLine(250, self)
        zoom_timeline.setUpdateInterval(15)
        zoom_timeline.setProperty("zoom_time_line_data", ZoomTimeLineData(zoom_factor))
        zoom_timeline.valueChanged.connect(self.on_zoom_timeline_value_changed)
        zoom_timeline.start()

    def on_zoom_timeline_value_changed(self, time_line_value):
        zoom_time_line_data: ZoomTimeLineData = self.sender().property("zoom_time_line_data")
        current_zoom = self.get_current_view_scale()
        time_line_value_delta = time_line_value - zoom_time_line_data.prev_time_line_value
        new_zoom = current_zoom * zoom_time_line_data.zoom_factor ** time_line_value_delta
        self.set_zoom_in_mouse_point(new_zoom)
        zoom_time_line_data.prev_time_line_value = time_line_value
        self.current.view_scene_top_left = self.mapToScene(self.viewport().rect().topLeft())
        self.last.view_scene_top_left = self.mapToScene(self.viewport().rect().topLeft())

    def set_zoom_in_mouse_point(self, new_zoom):
        m, top_left_old = self.current.mouse_scene_pos, self.current.view_scene_top_left
        old_zoom = self.get_current_view_scale()
        new_zoom = self.limit_new_zoom(new_zoom)

        top_left_new = m - (m - top_left_old) * old_zoom / new_zoom
        self.reset()
        # print("top_left", top_left_new.x())
        transform = QTransform().scale(new_zoom, new_zoom).translate(-top_left_new.x(), -top_left_new.y())
        self.setTransform(transform, False)
        self.zoomChanged.emit(self.get_current_view_scale())

    def set_zoom_in_view_center(self, new_zoom):
        new_zoom = self.limit_new_zoom(new_zoom)
        # view_scene_center = self.mapToScene(self.viewport().rect().center())
        view_scene_center = self.mapToScene(self.rect().center())
        self.reset()
        self.scale(new_zoom, new_zoom)
        self.centerOn(view_scene_center)
        self.zoomChanged.emit(self.get_current_view_scale())

    def limit_new_zoom(self, new_zoom):
        if new_zoom > self.max_zoom:
            new_zoom = self.max_zoom
        elif new_zoom < self.min_zoom:
            new_zoom = self.min_zoom
        return new_zoom

    def get_current_view_scale(self):
        scale = self.transform().m11()
        return scale

    def mouseMoveEvent(self, event: QtGui.QMouseEvent) -> None:
        self.pan = (self.current.mouse_pos - self.last.mouse_pos) / self.get_current_view_scale()
        self.mouse_move_timer = QTimer(self)
        self.mouse_move_timer.setInterval(0)
        self.mouse_move_timer.timeout.connect(self.on_almost_immediate_move)
        self.mouse_move_timer.setSingleShot(True)
        self.mouse_move_timer.start()
        event.accept()

    def on_almost_immediate_move(self):
        self.translate(self.pan.x(), self.pan.y())

    def mouseReleaseEvent(self, event: QtGui.QMouseEvent) -> None:
        if event.button() == Qt.LeftButton:
            if self.mouse_move_timer and self.mouse_move_timer.isActive():
                # print("release")
                self.mouse_move_timer.stop()
                self.launch_pan_time_line(self.pan * 3)
        event.accept()

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
