import time
import typing
from PyQt5 import QtGui, QtCore
from PyQt5.QtCore import QTimeLine, QMutex, QMutexLocker, QObject, Qt, QTimer, QPoint, QPointF, QRect, QRectF, \
    pyqtSignal
from PyQt5.QtGui import QTransform, QVector2D, QPainter, QMouseEvent, QWheelEvent, QResizeEvent
from PyQt5.QtWidgets import QGraphicsView, QGraphicsScene, QWidget

view_mutex = QMutex()
zoom_step_factor = 1.25


class ZoomTimeLineData():
    def __init__(self, zoom_factor):
        self.zoom_factor = zoom_factor
        self.prev_time_line_value = 0


class PanTimeLineData():
    def __init__(self, pan):
        self.pan = pan
        self.prev_time_line_value = 0


class SlideViewerGraphicsView(QGraphicsView):
    zoomChanged = pyqtSignal(float)

    def __init__(self, scene: QGraphicsScene, parent: typing.Optional[QWidget] = ...):
        super().__init__(scene, parent)
        self.setTransformationAnchor(QGraphicsView.NoAnchor)
        self.current_mouse_scene_pos = None
        self.current_view_scene_top_left = None
        self.current_view_scene_center = None
        self.current_view_scene_center = None
        self.current_mouse_pos = None
        self.last_mouse_scene_pos = None
        self.last_view_scene_top_left = None
        self.last_view_scene_center = None
        self.last_view_scene_center = None
        self.last_mouse_pos = None
        self.mouse_move_timer = None
        self.min_zoom = 1
        self.max_zoom = 2.5
        self.pan = None
        # self.setRenderHints(QPainter.Antialiasing | QPainter.SmoothPixmapTransform)

    def reset(self):
        self.resetTransform()
        self.horizontalScrollBar().setValue(0)
        self.verticalScrollBar().setValue(0)

    def fit_scene(self):
        self.reset()
        self.update_view_scene_rect_and_min_zoom()
        self.scale(self.min_zoom, self.min_zoom)
        self.centerOn(self.scene().sceneRect().center())
        self.zoomChanged.emit(self.get_current_view_scale())

    def viewportEvent(self, event: QtCore.QEvent) -> bool:
        current_rect = QRect(self.viewport().rect())
        if isinstance(event, QResizeEvent):
            current_rect.setSize(event.oldSize())
            self.current_view_scene_center = self.mapToScene(
                self.mapFromGlobal(self.mapToGlobal(current_rect.center())))
        else:
            self.current_view_scene_center = self.mapToScene(current_rect.center())

        # self.current_view_scene_center = self.mapToGlobal(current_rect.center()) / self.get_current_view_scale()
        self.current_view_scene_top_left = self.mapToScene(current_rect.topLeft())
        self.current_view_scene_center = self.mapToScene(current_rect.center())
        if isinstance(event, QMouseEvent) or isinstance(event, QWheelEvent):
            self.current_mouse_pos = event.pos()
            self.current_mouse_scene_pos = self.mapToScene(event.pos())
        res = super().viewportEvent(event)
        old_rect = current_rect
        current_rect = self.viewport().rect()

        if isinstance(event, QResizeEvent):
            current_rect.setSize(event.oldSize())
            self.last_view_scene_center = self.mapToScene(self.mapFromGlobal(self.mapToGlobal(current_rect.center())))
        else:
            self.last_view_scene_center = self.mapToScene(current_rect.center())

        self.last_view_scene_top_left = self.mapToScene(current_rect.topLeft())
        self.last_view_scene_center = self.mapToScene(current_rect.center())
        if isinstance(event, QMouseEvent) or isinstance(event, QWheelEvent):
            self.last_mouse_pos = event.pos()
            self.last_mouse_scene_pos = self.mapToScene(event.pos())
        new_rect = current_rect
        # print(old_rect, new_rect)
        return res

    def resizeEvent(self, a0: QtGui.QResizeEvent) -> None:
        self.update_view_scene_rect_and_min_zoom()
        view_scene_center_shift = self.last_view_scene_center - self.current_view_scene_center
        self.translate(view_scene_center_shift.x(), view_scene_center_shift.y())
        zoom = self.get_current_view_scale()
        if zoom < self.min_zoom:
            # print("zoom: {}, min_zoom:{}".format(zoom, self.min_zoom))
            self.fit_scene()

    def update_view_scene_rect_and_min_zoom(self):
        vw, vh = self.width(), self.height()
        # item_rect = self.slide_graphics_item.boundingRect()
        item_rect = self.scene().sceneRect()
        if item_rect:
            iw, ih = item_rect.width(), item_rect.height()
            a, b = vw / iw, vh / ih
            cw = 1.5 * max(1, a / b) * 1.1
            ch = 1.5 * max(1, b / a) * 1.1
            self.min_zoom = max(a / cw, b / ch)
            # print("min_zoom: {}".format(1 / self.min_zoom))
            sw, sh = iw * cw, ih * ch
            scrollable_area_rect = QRectF(0, 0, sw, sh)
            scrollable_area_rect.moveCenter(item_rect.center())
            self.setSceneRect(scrollable_area_rect)

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
        self.current_view_scene_top_left = self.mapToScene(self.viewport().rect().topLeft())
        self.last_view_scene_top_left = self.mapToScene(self.viewport().rect().topLeft())

    def set_zoom_in_mouse_point(self, new_zoom):
        m, top_left_old = self.current_mouse_scene_pos, self.current_view_scene_top_left
        old_zoom = self.get_current_view_scale()

        if new_zoom > self.max_zoom:
            new_zoom = self.max_zoom
        elif new_zoom < self.min_zoom:
            new_zoom = self.min_zoom

        top_left_new = m - (m - top_left_old) * old_zoom / new_zoom
        self.reset()
        # print("top_left", top_left_new.x())
        transform = QTransform().scale(new_zoom, new_zoom).translate(-top_left_new.x(), -top_left_new.y())
        self.setTransform(transform, False)
        self.zoomChanged.emit(self.get_current_view_scale())

    def set_zoom_in_view_center(self, new_zoom):
        if new_zoom > self.max_zoom:
            new_zoom = self.max_zoom
        elif new_zoom < self.min_zoom:
            new_zoom = self.min_zoom
        view_scene_center = self.mapToScene(self.viewport().rect().center())
        self.reset()
        self.scale(new_zoom, new_zoom)
        self.centerOn(view_scene_center)
        self.zoomChanged.emit(self.get_current_view_scale())

    # def scrollbar_issue(self):
    #     scrollbar_extent = QApplication.style().pixelMetric(QStyle.PM_ScrollBarExtent)
    #     scroll_pos = QPoint(scrollbar_extent, scrollbar_extent)
    #     view_bottom_right = self.view.mapToScene(self.view.rect().bottomRight() - scroll_pos) / min_zoom
    #     scene_bottom_rigth = self.view.sceneRect().bottomRight()
    #     diff = scene_bottom_rigth - view_bottom_right
    #     transform = QTransform().scale(min_zoom, min_zoom).translate(-diff.x() / 2, -diff.y() / 2)
    #     self.view.setTransform(transform, False)
    #     self.view.set_zoom_center(min_zoom)
    #     self.view_scene_center = self.view.mapToScene(self.view.rect().bottomRight())

    def get_current_view_scale(self):
        scale = self.transform().m11()
        return scale

    def mouseMoveEvent(self, event: QtGui.QMouseEvent) -> None:
        self.pan = (self.current_mouse_pos - self.last_mouse_pos) / self.get_current_view_scale()
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
        self.current_mouse_pos = self.last_mouse_pos + pan_time_line_data.pan * time_line_value_delta
        pan_time_line_data.prev_time_line_value = time_line_value

    def log_state(self):
        print("scene_rect: {} view_scene_rect: {} scale: {}".format(self.scene().sceneRect(), self.sceneRect(),
                                                                    self.get_current_view_scale()))
