import typing
from collections import OrderedDict

from PyQt5.QtGui import QBrush, QPen, QColor, QPixmapCache
from PyQt5.QtWidgets import QWidget, QGraphicsScene, QVBoxLayout, QGraphicsItemGroup, QHBoxLayout, QSplitter
from PyQt5.QtCore import Qt, QRectF, QEvent, QObject, QMimeData, pyqtSignal

from slide_viewer.config import debug, initial_scene_background_color
from slide_viewer.ui.annotation.annotation_utls import update_data_by_item, update_ordered_dict_by_data, \
    update_data_by_ordered_dict, update_item_by_data, ordered_dict_to_data
from slide_viewer.ui.annotation.annotation_data import AnnotationData
from slide_viewer.ui.dict_tree_view_model.ordered_dicts_tree_model import OrderedDictsTreeModel
from slide_viewer.ui.dict_tree_view_model.ordered_dicts_tree_widget import OrderedDictsTreeWidget
from slide_viewer.ui.slide.slide_graphics_grid_item import SlideGraphicsGridItem
from slide_viewer.ui.slide.slide_graphics_item import SlideGraphicsItem
from slide_viewer.slide_helper import SlideHelper
from slide_viewer.ui.slide.slide_viewer_graphics_view import SlideViewerGraphicsView


class SlideViewerWidget(QWidget):
    slideFileChanged = pyqtSignal(str)

    def __init__(self, parent: QWidget = None, on_slide_load_callback=None):
        super().__init__(parent)
        self.debug = debug
        self.slide_helper: SlideHelper = None
        self.on_slide_load_callback = on_slide_load_callback
        self.scene = QGraphicsScene(self)
        self.view = SlideViewerGraphicsView(self.scene, parent)
        self.view.setBackgroundBrush(QColor(initial_scene_background_color))
        self.view.setDisabled(True)
        self.slide_graphics_item = None
        self.slide_graphics_grid_item = None
        self.debug_view_scene_rect = None
        self.item_debug_rect = None
        # self.view.log_state()
        self.layout = QHBoxLayout(self)
        self.setLayout(self.layout)
        self.odicts_widget = OrderedDictsTreeWidget(self)

        self.splitter = QSplitter()
        self.splitter.addWidget(self.view)
        self.splitter.addWidget(self.odicts_widget)
        self.layout.addWidget(self.splitter)
        self.splitter.setStretchFactor(0, 1)
        self.splitter.setStretchFactor(1, 0)

        self.scene.installEventFilter(self)
        self.view.minScaleChanged.connect(self.on_min_zoom_changed)

        self.view.annotationItemAdded.connect(self.on_annotation_item_added)
        self.view.annotationItemsSelected.connect(self.on_annotation_items_selected)
        self.odicts_widget.view.odictsChanged.connect(self.on_odicts_changed)
        self.odicts_widget.view.odictsRemoved.connect(self.on_odicts_removed)
        self.odicts_widget.view.odictSelected.connect(self.on_odict_selected)

    def eventFilter(self, target: QObject, event: QEvent) -> bool:
        drag_events = [QEvent.GraphicsSceneDragEnter, QEvent.GraphicsSceneDragMove]
        drop_events = [QEvent.GraphicsSceneDrop]
        if event.type() in drag_events and SlideViewerWidget.mime_data_is_url(event.mimeData()):
            event.accept()
            return True
        elif event.type() in drop_events and SlideViewerWidget.mime_data_is_url(event.mimeData()):
            file_path = event.mimeData().urls()[0].toLocalFile()
            # print(file_path)
            self.load(file_path)
            event.accept()
            return True

        return super().eventFilter(target, event)

    @staticmethod
    def mime_data_is_url(mime_data: QMimeData):
        return mime_data.hasUrls() and len(mime_data.urls()) == 1

    def load(self, file_path):
        QPixmapCache.clear()
        self.slide_helper = SlideHelper(file_path)
        self.view.microns_per_pixel = self.slide_helper.microns_per_pixel

        self.view.on_off_annotation_item()
        self.view.reset_annotation_items()
        self.odicts_widget.view.setModel(OrderedDictsTreeModel())

        self.scene.clear()
        self.scene.setSceneRect(self.slide_helper.get_rect_for_level(0))
        self.slide_graphics_item = SlideGraphicsItem(file_path)
        self.scene.addItem(self.slide_graphics_item)
        unlimited_rect = QRectF(-2 ** 31, -2 ** 31, 2 ** 32, 2 ** 32)
        self.view.setSceneRect(unlimited_rect)
        self.view.update_fit_and_min_scale()
        # self.update_debug_item_rect()
        self.view.fit_scene()

        self.slide_graphics_grid_item = SlideGraphicsGridItem(self.slide_graphics_item.boundingRect(),
                                                              self.view.min_scale, self.view.max_scale)
        self.scene.addItem(self.slide_graphics_grid_item)

        self.view.setDisabled(False)
        self.slideFileChanged.emit(file_path)

    def on_min_zoom_changed(self, new_min_zoom):
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

    def on_annotation_item_added(self, annotation_item: QGraphicsItemGroup):
        data = annotation_item.annotation_data
        # data = AnnotationData()
        # update_data_by_item(annotation_item, data)
        odict = OrderedDict()
        update_ordered_dict_by_data(data, odict)
        # print(odict)
        self.odicts_widget.view.model().add_odict(odict)

    def on_annotation_items_selected(self, item_numbers: list):
        if item_numbers:
            first_odict_number = item_numbers[0]
            self.odicts_widget.view.select_odict(first_odict_number)
        else:
            self.odicts_widget.view.clear_selection()

    def on_odicts_removed(self, odict_numbers: list):
        for odict_number in odict_numbers:
            item = self.view.annotation_items[odict_number]
            self.scene.removeItem(item)
            del self.view.annotation_items[odict_number]

    def on_odicts_changed(self, odict_numbers: list):
        for odict_number in odict_numbers:
            # full replacing of dict is implemented as:
            # beginRemoveRows()->replace dict with empty dict->endRemoveRows()->beginInsertRows()->set new dict->endInsertRows()
            # so we can have empty dict here, but can ignore it
            odict = self.odicts_widget.view.model().odicts[odict_number]
            if odict:
                data = ordered_dict_to_data(odict)
                item = self.view.annotation_items[odict_number]
                update_item_by_data(item, data)

    def on_odict_selected(self, dict_num: int):
        for item in self.view.annotation_items:
            item.setSelected(False)
        item = self.view.annotation_items[dict_num]
        item.setSelected(True)
