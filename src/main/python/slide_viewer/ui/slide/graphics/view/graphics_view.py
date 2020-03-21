from typing import Optional, Tuple, cast

from PyQt5 import QtGui
from PyQt5.QtCore import QObject, Qt, pyqtSignal, QEvent, QRectF
from PyQt5.QtGui import QMouseEvent, QBrush
from PyQt5.QtWidgets import QGraphicsView, QWidget, QGraphicsSceneDragDropEvent
from dataclasses import dataclass, field

from common.debug_only_decorator import debug_only
from common_qt.abcq_meta import ABCQMeta
from common_qt.graphics.graphics_item_debug_rect import GraphicsItemDebugRect
from common_qt.graphics.graphics_view_debug_rect import \
    GraphicsViewDebugRect
from common_qt.grid_graphics_item import GridGraphicsItem
from common_qt.key_press_util import KeyPressEventUtil
from common_qt.mime_utils import mime_data_is_url
from slide_viewer.common.slide_helper import SlideHelper
from slide_viewer.ui.slide.graphics.graphics_scene import GraphicsScene
from slide_viewer.ui.slide.graphics.help_utils import empty_view_help_text
from slide_viewer.ui.slide.graphics.item.filter_graphics_item import FilterGraphicsItem
from slide_viewer.ui.slide.graphics.item.slide_graphics_item import SlideGraphicsItem
from slide_viewer.ui.slide.graphics.view.graphics_view_annotation_service import GraphicsViewAnnotationService
from slide_viewer.ui.slide.graphics.view.graphics_view_annotation_service2 import GraphicsViewAnnotationService2
from slide_viewer.ui.slide.graphics.view.scale_graphics_view import ScaleGraphicsView
from slide_viewer.ui.slide.widget.interface.annotation_pixmap_provider import AnnotationItemPixmapProvider
from slide_viewer.ui.slide.widget.interface.annotation_service import AnnotationService
from slide_viewer.ui.slide.widget.interface.slide_stats_provider import SlideStatsProvider


@dataclass(repr=False)
class GraphicsView(ScaleGraphicsView, SlideStatsProvider, metaclass=ABCQMeta):
    # graphics_view_annotation_service: GraphicsViewAnnotationService = ...
    graphics_view_annotation_service: GraphicsViewAnnotationService2 = ...
    annotation_pixmap_provider: AnnotationItemPixmapProvider = ...
    _grid_size: Tuple[int, int] = (512, 512)
    _grid_size_is_in_pixels: bool = True
    slide_helper: Optional[SlideHelper] = field(init=False, default=None)
    slide_graphics_item: Optional[SlideGraphicsItem] = field(init=False, default=None)
    filter_graphics_item: Optional[FilterGraphicsItem] = field(init=False, default=None)
    slide_graphics_grid_item: Optional[GridGraphicsItem] = field(init=False, default=None)

    gridVisibleChanged = pyqtSignal(bool)
    gridSizeChanged = pyqtSignal(tuple)
    gridSizeIsInPixelsChanged = pyqtSignal(bool)
    filePathChanged = pyqtSignal(str)
    filePathDropped = pyqtSignal(str)
    backgroundBrushChanged = pyqtSignal(QBrush)

    def __post_init__(self, parent_: Optional[QWidget]):
        ScaleGraphicsView.__post_init__(self, parent_)
        self.id = None  # debug purpose
        scene = GraphicsScene(parent_=self)
        self.setScene(scene)
        self.scene().installEventFilter(self)
        self.scene().sceneRectChanged.connect(self.update_min_scale)
        self.scene().addText(empty_view_help_text)
        self.setDisabled(True)
        self.gridSizeChanged.connect(self.update_grid_item)
        self.gridSizeIsInPixelsChanged.connect(self.update_grid_item)

    @property
    def annotation_service(self) -> AnnotationService:
        return self.graphics_view_annotation_service.annotation_service

    def get_microns_per_pixel(self) -> float:
        return self.slide_helper.microns_per_pixel

    def get_background_brush(self) -> QBrush:
        return self.backgroundBrush()

    def set_background_brush(self, brush: QBrush) -> None:
        QGraphicsView.setBackgroundBrush(self, brush)
        self.backgroundBrushChanged.emit(brush)

    setBackgroundBrush = None

    def get_grid_visible(self) -> bool:
        return self.slide_graphics_grid_item is not None and self.slide_graphics_grid_item.isVisible()

    def set_grid_visible(self, visible: bool) -> None:
        # print(f'self: {id(self)}, sender: {id(self.sender())}')
        self.slide_graphics_grid_item.setVisible(visible)
        self.gridVisibleChanged.emit(visible)

    def get_grid_size(self) -> Tuple[int, int]:
        return self._grid_size

    def set_grid_size(self, size: Tuple[int, int]) -> None:
        self._grid_size = size
        self.gridSizeChanged.emit(size)

    def get_grid_size_is_in_pixels(self) -> bool:
        return self._grid_size_is_in_pixels

    def set_grid_size_is_in_pixels(self, grid_size_is_in_pixels: bool) -> None:
        self._grid_size_is_in_pixels = grid_size_is_in_pixels
        self.gridSizeIsInPixelsChanged.emit(grid_size_is_in_pixels)

    def get_file_path(self) -> str:
        return self.slide_helper.slide_path

    def set_file_path(self, file_path: str) -> None:
        self.slide_helper = SlideHelper(file_path)
        self.graphics_view_annotation_service.cancel_annotation_if_any()
        self.scene().clear()
        self.scene().setSceneRect(self.slide_helper.get_rect_for_level(0))
        unlimited_rect = QRectF(-2 ** 31, -2 ** 31, 2 ** 32, 2 ** 32)
        self.setSceneRect(unlimited_rect)
        # self.view.update_fit_and_min_scale()
        self.fit_scene()

        self.slide_graphics_item = SlideGraphicsItem(file_path)
        self.scene().addItem(self.slide_graphics_item)

        self.slide_graphics_grid_item = GridGraphicsItem(bounding_rect=self.slide_graphics_item.boundingRect())
        self.update_grid_item()
        self.scene().addItem(self.slide_graphics_grid_item)

        self.filter_graphics_item = FilterGraphicsItem(self.annotation_pixmap_provider, self.slide_helper)
        self.scene().addItem(self.filter_graphics_item)

        self.filePathChanged.emit(file_path)
        self.update()

    def update_grid_item(self):
        if self.slide_helper and self.slide_graphics_grid_item:
            if self.get_grid_size_is_in_pixels():
                grid_size_in_pixels = self.get_grid_size()
            else:
                w = self.slide_helper.microns_to_pixels(self.get_grid_size()[0])
                h = self.slide_helper.microns_to_pixels(self.get_grid_size()[1])
                grid_size_in_pixels = (w, h)
            self.slide_graphics_grid_item.grid_size = grid_size_in_pixels
            self.slide_graphics_grid_item.update_lines()
            self.slide_graphics_grid_item.update()

    def scene(self) -> GraphicsScene:
        return cast(GraphicsScene, super().scene())

    def eventFilter(self, source: QObject, event: QEvent) -> bool:
        print(self.hasMouseTracking())
        res=self.graphics_view_annotation_service.eventFilter(source, event)
        if res:
            return True
        if isinstance(event, QGraphicsSceneDragDropEvent):
            drag_events = [QEvent.GraphicsSceneDragEnter, QEvent.GraphicsSceneDragMove]
            drop_events = [QEvent.GraphicsSceneDrop]
            if event.type() in drag_events and mime_data_is_url(event.mimeData()):
                event.accept()
                return True
            elif event.type() in drop_events and mime_data_is_url(event.mimeData()):
                file_path = event.mimeData().urls()[0].toLocalFile()
                self.set_file_path(file_path)
                self.filePathDropped.emit(file_path)
                event.accept()
                return True
            else:
                return False
        else:
            # print("super", event)
            return super().eventFilter(source, event)

    def log_state(self) -> None:
        print("scene_rect: {} view_scene_rect: {} scale: {}".format(self.scene().sceneRect(), self.sceneRect(),
                                                                    self.get_current_view_scale()))

    @debug_only()
    def init_debug_scene_view_rect(self) -> None:
        self.filePathChanged.connect(lambda: self.scene().addItem(GraphicsViewDebugRect(self.view)))

    @debug_only()
    def init_debug_item_rect(self) -> None:
        self.filePathChanged.connect(
            lambda: self.scene().addItem(GraphicsItemDebugRect(self.slide_graphics_item)))
