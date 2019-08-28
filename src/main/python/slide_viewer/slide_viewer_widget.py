from PyQt5 import QtGui, QtCore
from PyQt5.QtGui import QBrush, QPen, QColor, QPixmapCache, QTransform, QDropEvent, QDragMoveEvent, QDragEnterEvent
from PyQt5.QtWidgets import QWidget, QGraphicsScene, QVBoxLayout, QCommonStyle, QStyle, QApplication, \
    QGraphicsSceneDragDropEvent
from PyQt5.QtCore import Qt, QRectF, QPointF, QPoint, QEvent, QObject, QMimeData, pyqtSignal

from slide_viewer.config import debug, initial_scene_background_color
from slide_viewer.slide_graphics_grid_item import SlideGraphicsGridItem
from slide_viewer.slide_graphics_item import SlideGraphicsItem
from slide_viewer.slide_helper import SlideHelper
from slide_viewer.slide_viewer_graphics_view import SlideViewerGraphicsView


class SlideViewerWidget(QWidget):
    slideFileChanged = pyqtSignal(str)

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

        self.scene.installEventFilter(self)
        self.view.minZoomChanged.connect(self.onMinZoomChanged)

    def eventFilter(self, target: QObject, event: QEvent) -> bool:
        drag_events = [QEvent.GraphicsSceneDragEnter, QEvent.GraphicsSceneDragMove]
        drop_events = [QEvent.GraphicsSceneDrop]
        if event.type() in drag_events and self.mime_data_is_url(event.mimeData()):
            event.accept()
            return True
        elif event.type() in drop_events and self.mime_data_is_url(event.mimeData()):
            file_path = event.mimeData().urls()[0].toLocalFile()
            # print(file_path)
            self.load(file_path)
            event.accept()
            return True

        return super().eventFilter(target, event)

    def mime_data_is_url(self, mime_data: QMimeData):
        return mime_data.hasUrls() and len(mime_data.urls()) == 1

    def load(self, file_path):
        QPixmapCache.clear()
        self.slide_helper = SlideHelper(file_path)

        self.scene.clear()
        self.scene.setSceneRect(self.slide_helper.get_rect_for_level(0))

        self.slide_graphics_item = SlideGraphicsItem(file_path)
        self.scene.addItem(self.slide_graphics_item)
        unlimited_rect = QRectF(-2 ** 31, -2 ** 31, 2 ** 32, 2 ** 32)
        self.view.setSceneRect(unlimited_rect)
        self.view.update_fit_and_min_zoom()
        # self.update_debug_item_rect()
        self.view.fit_scene()

        self.slide_graphics_grid_item = SlideGraphicsGridItem(self.slide_graphics_item.boundingRect(),
                                                              self.view.min_zoom, self.view.max_zoom)
        self.scene.addItem(self.slide_graphics_grid_item)
        self.slideFileChanged.emit(file_path)

    def onMinZoomChanged(self, new_min_zoom):
        if self.slide_graphics_grid_item:
            self.slide_graphics_grid_item.min_zoom = new_min_zoom

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
