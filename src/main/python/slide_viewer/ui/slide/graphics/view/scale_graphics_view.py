from typing import Optional

from PyQt5 import QtGui
from PyQt5.QtCore import Qt, QPointF, pyqtSignal, QEvent, QPoint, QRectF, QTimer
from PyQt5.QtGui import QTransform, QMouseEvent, QWheelEvent, QResizeEvent, QCursor
from PyQt5.QtWidgets import QGraphicsView, QWidget
from dataclasses import dataclass, field, InitVar

from common_qt.abcq_meta import ABCQMeta
from common_qt.almost_immediate_timer import AlmostImmediateTimer
from common_qt.graphics_view_transform_notifier import GraphicsViewTransformNotifier
from slide_viewer.ui.common.timeline.pan_time_line import PanTimeLine, PanTimeLineData
from slide_viewer.ui.common.timeline.scale_time_line import ScaleTimeLineData, ScaleTimeLine
from slide_viewer.ui.slide.graphics.view.view_params import ViewParams
from slide_viewer.ui.slide.widget.interface.scale_view_provider import ScaleProvider


@dataclass
class ScaleGraphicsView(GraphicsViewTransformNotifier, ScaleProvider, metaclass=ABCQMeta):
    parent_: InitVar[Optional[QWidget]] = field(default=None)
    min_scale: float = 1
    max_scale: float = 5
    scale_step_factor: float = 1.25
    max_items_per_screen: float = 1.5
    pan_strength_factor: float = 3
    current: ViewParams = field(default_factory=ViewParams)
    last: ViewParams = field(default_factory=ViewParams)
    mouse_move_timer: Optional[QTimer] = None
    scheduled_pan: Optional[QPoint] = None
    scaleChanged = pyqtSignal(float)

    def __post_init__(self, parent_: Optional[QWidget]):
        super().__init__(parent_)
        self.setTransformationAnchor(QGraphicsView.NoAnchor)
        self.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)

    def get_scale(self):
        return self.get_current_view_scale()

    def get_current_view_scale(self) -> float:
        return self.transform().m11()

    def update_min_scale(self) -> None:
        fit_scale = self.get_scale_to_fit_rect(self.scene().sceneRect())
        self.min_scale = fit_scale / self.max_items_per_screen

    def get_scale_to_fit_rect(self, rect: QRectF) -> float:
        vw, vh = self.width(), self.height()
        if rect and rect.width() and rect.height():
            iw, ih = rect.width(), rect.height()
            fit_scale = min(vw / iw, vh / ih)
            return fit_scale
        else:
            return 1

    def limit_new_scale(self, new_scale: float) -> float:
        if new_scale > self.max_scale:
            new_scale = self.max_scale
        elif new_scale < self.min_scale:
            new_scale = self.min_scale
        return new_scale

    def viewportEvent(self, event: QEvent) -> bool:
        self.update_view_params(event, self.current)
        res = super().viewportEvent(event)
        self.update_view_params(event, self.last)
        if event.type() == QEvent.Resize:
            self.update_min_scale()
        return res

    def update_view_params(self, event: QEvent, view_params: ViewParams) -> None:
        rect = self.viewport().rect()
        if isinstance(event, QResizeEvent):
            rect.setSize(event.oldSize())

        if isinstance(event, QMouseEvent) or isinstance(event, QWheelEvent):
            view_params.mouse_pos = event.pos()
            view_params.mouse_scene_pos = self.mapToScene(event.pos())
            if event.type() == QEvent.MouseMove:
                view_params.mouse_move_between_press_and_release = True
            elif event.type() == QEvent.MouseButtonPress:
                view_params.mouse_move_between_press_and_release = False

    def wheelEvent(self, event: QtGui.QWheelEvent) -> None:
        steps_count = abs(event.angleDelta().y()) / 120
        is_scale_in = event.angleDelta().y() > 0
        scale_factor_ = self.scale_step_factor if is_scale_in else 1 / self.scale_step_factor
        scale_factor = scale_factor_ ** steps_count
        self.launch_scale_time_line(scale_factor)
        event.accept()

    def launch_scale_time_line(self, scale_factor: float) -> None:
        timeline = ScaleTimeLine(parent=self, scale_factor=scale_factor,
                                 value_changed_callback=self.__on_scale_timeline_value_changed)
        timeline.start()

    def __on_scale_timeline_value_changed(self, time_line_value: float, data: ScaleTimeLineData) -> None:
        current_scale = self.get_current_view_scale()
        time_line_value_delta = time_line_value - data.prev_time_line_value
        new_scale = current_scale * data.scale_factor ** time_line_value_delta
        current_mouse_pos = self.mapFromGlobal(QCursor().pos())
        # self.set_scale_in_mouse_point(new_scale, self.current.mouse_pos)
        self.set_scale_in_mouse_point(new_scale, current_mouse_pos)
        # self.set_scale_in_scene_point(new_scale, self.mapToScene(current_mouse_pos))
        data.prev_time_line_value = time_line_value

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

    def set_scale_in_scene_point(self, new_scale: float, scene_point: QPointF) -> None:
        new_scale = self.limit_new_scale(new_scale)
        self.resetTransform()
        self.scale(new_scale, new_scale)
        shift = scene_point - self.mapToScene(self.rect().bottomRight()) / 2
        self.translate(-shift.x(), -shift.y())

    def set_scale_in_view_center(self, new_scale: float) -> None:
        view_scene_center = self.mapToScene(self.rect().center())
        self.set_scale_in_scene_point(new_scale, view_scene_center)

    def fit_scene(self) -> None:
        self.fit_rect(self.scene().sceneRect())

    def fit_rect(self, rect: QRectF) -> None:
        fit_scale = self.get_scale_to_fit_rect(rect)
        self.set_scale_in_scene_point(fit_scale, rect.center())

    def mouseMoveEvent(self, event: QtGui.QMouseEvent) -> None:
        if int(event.buttons()) & Qt.LeftButton == Qt.LeftButton and not self.scene().mouseGrabberItem():
            self.scheduled_pan = (self.current.mouse_pos - self.last.mouse_pos) / self.get_current_view_scale()
            self.mouse_move_timer = AlmostImmediateTimer(self, self.__on_almost_immediate_move)
            self.mouse_move_timer.start()
            event.accept()
        else:
            super().mouseMoveEvent(event)

    def __on_almost_immediate_move(self) -> None:
        self.translate(self.scheduled_pan.x(), self.scheduled_pan.y())

    def mouseReleaseEvent(self, event: QMouseEvent) -> None:
        super().mouseReleaseEvent(event)
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

    def on_mouse_click(self, event: QMouseEvent) -> bool:
        return False

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
