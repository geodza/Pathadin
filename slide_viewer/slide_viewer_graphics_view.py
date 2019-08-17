import typing
from PyQt5 import QtGui
from PyQt5.QtCore import QTimeLine
from PyQt5.QtGui import QTransform
from PyQt5.QtWidgets import QGraphicsView, QGraphicsScene, QWidget


class SlideViewerGraphicsView(QGraphicsView):

    def __init__(self, scene: QGraphicsScene, parent: typing.Optional[QWidget] = ...):
        super().__init__(scene, parent)
        self.setTransformationAnchor(QGraphicsView.NoAnchor)
        self.scale_steps = 0
        self.scale_mouse_scene_pos = None
        self.scale_view_scene_top_left = None
        self.scale_timeline = QTimeLine(200, self)
        self.scale_timeline.valueChanged.connect(self.on_scale_timeline_value_changed)

    def on_scale_timeline_value_changed(self):
        zoom_factor = 1.0 + self.scale_steps / 8.0
        self.zoom(zoom_factor)

    def zoom(self, zoom_factor):
        m, top_left_old = self.scale_mouse_scene_pos, self.scale_view_scene_top_left
        top_left_new = m - (m - top_left_old) / zoom_factor
        new_scale = self.get_current_view_scale() * zoom_factor
        self.horizontalScrollBar().setValue(0)
        self.verticalScrollBar().setValue(0)
        transform = QTransform().scale(new_scale, new_scale).translate(-top_left_new.x(), -top_left_new.y())
        self.setTransform(transform, False)
        self.scale_view_scene_top_left = top_left_new

    def get_current_view_scale(self):
        scale = self.transform().m11()
        return scale

    def wheelEvent(self, event: QtGui.QWheelEvent) -> None:
        scale_steps = event.angleDelta().y() / 120
        self.scale_steps = scale_steps
        # print("wheelEvent", event, scale_steps)
        self.scale_mouse_scene_pos = self.mapToScene(event.pos())
        self.scale_view_scene_top_left = self.mapToScene(self.viewport().rect().topLeft())
        self.scale_timeline.stop()
        self.scale_timeline.start()
        event.accept()

    def log_state(self):
        print("scene_rect: {} view_scene_rect: {} scale: {}".format(self.scene().sceneRect(), self.sceneRect(),
                                                                    self.get_current_view_scale()))
