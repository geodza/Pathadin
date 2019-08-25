from PyQt5 import QtGui, QtCore
from PyQt5.QtGui import QBrush, QPen, QColor, QPixmapCache, QTransform
from PyQt5.QtWidgets import QWidget, QGraphicsScene, QVBoxLayout, QCommonStyle, QStyle, QApplication
from PyQt5.QtCore import Qt, QRectF, QPointF, QPoint, QEvent

from slide_viewer.config import debug, initial_scene_background_color
from slide_viewer.slide_graphics_grid_item import SlideGraphicsGridItem
from slide_viewer.slide_graphics_item import SlideGraphicsItem
from slide_viewer.slide_helper import SlideHelper
from slide_viewer.slide_viewer_graphics_view import SlideViewerGraphicsView


class SlideViewerWidget(QWidget):

    def __init__(self, parent: QWidget = None, on_slide_load_callback=None):
        super().__init__(parent)
        self.debug = debug
        self.slide_helper = None
        self.on_slide_load_callback = on_slide_load_callback
        self.scene = QGraphicsScene(self)
        self.view = SlideViewerGraphicsView(self.scene, parent)
        self.view.setBackgroundBrush(QColor(initial_scene_background_color))
        self.slide_graphics_item = None
        self.slide_graphics_grid_item = None
        self.debug_view_scene_rect = None
        self.item_debug_rect = None
        # self.view.log_state()
        self.layout = QVBoxLayout(self)
        self.layout.addWidget(self.view)
        self.setLayout(self.layout)

        self.view_top_left = None
        self.view_scene_center = None

    def load(self, file_path):
        QPixmapCache.clear()
        self.slide_helper = SlideHelper(file_path)

        self.scene.clear()
        self.scene.setSceneRect(self.slide_helper.get_rect_for_level(0))

        self.slide_graphics_item = SlideGraphicsItem(file_path)
        self.scene.addItem(self.slide_graphics_item)
        # self.update_debug_item_rect()
        self.view.fit_scene()

        self.slide_graphics_grid_item = SlideGraphicsGridItem(self.slide_graphics_item.boundingRect(),
                                                              self.view.min_zoom, self.view.max_zoom)
        self.scene.addItem(self.slide_graphics_grid_item)
        return

    # def resizeEvent(self, a0: QtGui.QResizeEvent) -> None:
    #     if self.slide_graphics_item:
    #         self.update_view_scene_rect_and_min_zoom()
    # zoom = self.view.get_current_view_scale()
    # if zoom < self.min_zoom:
    #     print("zoom: {}, min_zoom:{}".format(zoom, self.min_zoom))
    #     self.view.set_zoom_center(self.min_zoom)

    # def event(self, a0: QtCore.QEvent) -> bool:
    #     acc = super().event(a0)
    #     if a0.type() != QEvent.Resize:
    #         if self.scene and self.view:
    #             self.view_scene_center = self.view.mapToScene(self.view.rect().center())
    #     return acc

    def update_debug_view_scene_rect(self):
        if self.debug:
            if self.debug_view_scene_rect:
                self.scene.removeItem(self.debug_view_scene_rect)
            qpen = QPen(QBrush(Qt.magenta), 200)
            qbrush = QBrush(QColor.fromRgb(0, 0, 0, 55))
            self.debug_view_scene_rect = self.scene.addRect(self.view.sceneRect(), qpen, qbrush)
            self.debug_view_scene_rect.setZValue(100)

    def update_debug_item_rect(self):
        if self.debug:
            if self.item_debug_rect:
                self.scene.removeItem(self.item_debug_rect)
            qpen = QPen(QBrush(Qt.darkCyan), 300)
            qbrush = QBrush(QColor.fromRgb(255, 0, 0, 55))
            item_rect = self.slide_graphics_item.boundingRect()
            self.item_debug_rect = self.scene.addRect(item_rect, qpen, qbrush)
            self.item_debug_rect.setPos(self.slide_graphics_item.pos())
            self.item_debug_rect.setZValue(100)
