from PyQt5.QtGui import QBrush, QPen, QColor, QPixmapCache
from PyQt5.QtWidgets import QWidget, QGraphicsScene, QVBoxLayout
from PyQt5.QtCore import Qt

from slide_viewer.config import debug
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
        self.slide_graphics_item = None
        # self.view.log_state()
        self.layout = QVBoxLayout(self)
        self.layout.addWidget(self.view)
        self.setLayout(self.layout)

    def load(self, file_path):
        QPixmapCache.clear()
        self.slide_helper = SlideHelper(file_path)
        self.view.resetTransform()
        self.scene.clear()
        self.scene.setSceneRect(self.slide_helper.get_rect_for_level(0))
        self.slide_graphics_item = SlideGraphicsItem(file_path)
        self.scene.addItem(self.slide_graphics_item)
        if self.on_slide_load_callback:
            self.on_slide_load_callback()

    def add_debug_scene_rect(self):
        if self.debug:
            qpen = QPen(QBrush(Qt.magenta), 20)
            qbrush = QBrush(QColor.fromRgb(0, 0, 0, 55))
            r1 = self.scene.addRect(self.scene.sceneRect(), qpen, qbrush)
            r1.setZValue(100)
