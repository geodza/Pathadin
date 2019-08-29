import time
import typing
from PyQt5 import QtGui, QtCore
from PyQt5.QtCore import QTimeLine, QMutex, QMutexLocker, QObject, Qt, QTimer, QPoint, QPointF, QRect, QRectF, \
    pyqtSignal, QEvent
from PyQt5.QtGui import QTransform, QVector2D, QPainter, QMouseEvent, QWheelEvent, QResizeEvent
from PyQt5.QtWidgets import QGraphicsView, QGraphicsScene, QWidget

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
