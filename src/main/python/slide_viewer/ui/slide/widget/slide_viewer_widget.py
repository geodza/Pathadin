from PyQt5.QtGui import QColor, QPixmapCache
from PyQt5.QtWidgets import QWidget, QGraphicsScene, QHBoxLayout, QSplitter, QGraphicsItemGroup, QGraphicsItem, \
    QGraphicsRectItem
from PyQt5.QtCore import QRectF, QEvent, QObject, pyqtSignal

from slide_viewer.config import initial_scene_background_color
from slide_viewer.ui.common.common import mime_data_is_url, debug_only
from slide_viewer.ui.dict_tree_view_model.config import is_instance_selectable, is_instance_editable, \
    create_instances_model, create_templates_model, create_default_instance_odict
from slide_viewer.ui.dict_tree_view_model.ordered_dicts_tree_model import OrderedDictsTreeModel
from slide_viewer.ui.dict_tree_view_model.ordered_dicts_tree_widget import OrderedDictsTreeWidget
from slide_viewer.ui.dict_tree_view_model.standard_attr_key import readonly_standard_attr_keys, StandardAttrKey
from slide_viewer.ui.slide.graphics.annotation.annotation_data import AnnotationData
from slide_viewer.ui.slide.graphics.annotation.annotation_path_item import AnnotationPathItem
from slide_viewer.ui.slide.graphics.slide_graphics_grid_item import SlideGraphicsGridItem
from slide_viewer.ui.slide.graphics.slide_graphics_item import SlideGraphicsItem
from slide_viewer.slide_helper import SlideHelper
from slide_viewer.ui.slide.graphics.slide_graphics_debug_item_rect import SlideGraphicsDebugItemRect
from slide_viewer.ui.slide.graphics.slide_graphics_debug_view_scene_rect import SlideGraphicsDebugViewSceneRect
from slide_viewer.ui.slide.graphics.slide_viewer_graphics_view import SlideViewerGraphicsView


class SlideViewerWidget(QWidget):
    slideFileChanged = pyqtSignal(str)

    def __init__(self, parent: QWidget = None):
        super().__init__(parent)
        self.slide_helper: SlideHelper = None

        self.setLayout(QHBoxLayout(self))

        self.scene = QGraphicsScene(self)
        self.scene.installEventFilter(self)

        self.slide_graphics_item = None
        self.slide_graphics_grid_item = None

        def odict_factory():
            for odict in self.odicts_widget.templates_view.model().odicts:
                if odict[StandardAttrKey.default_template.name]:
                    odict_copy = create_default_instance_odict(odict)
                    odict_copy.pop(StandardAttrKey.default_template.name, None)
                    odict_copy.pop(StandardAttrKey.area.name, None)
                    odict_copy.pop(StandardAttrKey.length.name, None)
                    odict_copy.pop(StandardAttrKey.annotation_type.name, None)
                    return odict_copy
            return create_default_instance_odict()

        self.view = SlideViewerGraphicsView(self.scene, odict_factory, parent)
        self.view.setBackgroundBrush(QColor(initial_scene_background_color))
        self.view.setDisabled(True)
        self.view.minScaleChanged.connect(self.on_min_zoom_changed)
        self.view.annotationItemAdded.connect(self.on_annotation_item_added)
        self.view.annotationItemsSelected.connect(self.on_annotation_items_selected)

        # self.view.log_state()

        self.odicts_widget = OrderedDictsTreeWidget(self)

        splitter = QSplitter()
        splitter.addWidget(self.view)
        splitter.addWidget(self.odicts_widget)
        splitter.setStretchFactor(0, 1)
        splitter.setStretchFactor(1, 0)
        self.layout().addWidget(splitter)

        self.odicts_widget.instances_view.odictsChanged.connect(self.on_odicts_changed)
        self.odicts_widget.instances_view.odictsInserted.connect(self.on_odicts_inserted)
        self.odicts_widget.instances_view.odictsRemoved.connect(self.on_odicts_removed)
        self.odicts_widget.instances_view.odictSelected.connect(self.on_odicts_selected)

        # self.odicts_widget.templates_view.odictSelected.connect(self.on_odicts_selected)

        self.init_debug_scene_view_rect()
        self.init_debug_item_rect()

    def eventFilter(self, target: QObject, event: QEvent) -> bool:
        drag_events = [QEvent.GraphicsSceneDragEnter, QEvent.GraphicsSceneDragMove]
        drop_events = [QEvent.GraphicsSceneDrop]
        if event.type() in drag_events and mime_data_is_url(event.mimeData()):
            event.accept()
            return True
        elif event.type() in drop_events and mime_data_is_url(event.mimeData()):
            file_path = event.mimeData().urls()[0].toLocalFile()
            # print(file_path)
            self.load(file_path)
            event.accept()
            return True

        return super().eventFilter(target, event)

    def load(self, file_path):
        QPixmapCache.clear()
        self.slide_helper = SlideHelper(file_path)
        self.view.microns_per_pixel = self.slide_helper.microns_per_pixel

        self.view.on_off_annotation_item()
        self.view.reset_annotation_items()

        instances_model = create_instances_model([])
        templates_model = create_templates_model([])
        self.odicts_widget.instances_view.setModel(instances_model)
        self.odicts_widget.templates_view.setModel(templates_model)

        self.scene.clear()
        self.scene.setSceneRect(self.slide_helper.get_rect_for_level(0))
        unlimited_rect = QRectF(-2 ** 31, -2 ** 31, 2 ** 32, 2 ** 32)
        self.view.setSceneRect(unlimited_rect)
        # self.view.update_fit_and_min_scale()
        self.view.fit_scene()

        self.slide_graphics_item = SlideGraphicsItem(file_path)
        self.scene.addItem(self.slide_graphics_item)
        self.slide_graphics_grid_item = SlideGraphicsGridItem(self.slide_graphics_item.boundingRect(),
                                                              self.view.min_scale, self.view.max_scale)
        self.scene.addItem(self.slide_graphics_grid_item)

        self.view.setDisabled(False)
        self.slideFileChanged.emit(file_path)

    def on_min_zoom_changed(self, new_min_zoom):
        if self.slide_graphics_grid_item:
            self.slide_graphics_grid_item.min_zoom = new_min_zoom

    @debug_only()
    def init_debug_scene_view_rect(self):
        self.slideFileChanged.connect(lambda: self.scene.addItem(SlideGraphicsDebugViewSceneRect(self.view)))

    @debug_only()
    def init_debug_item_rect(self):
        self.slideFileChanged.connect(lambda: self.scene.addItem(SlideGraphicsDebugItemRect(self.slide_graphics_item)))

    def on_annotation_item_added(self, annotation_item: AnnotationPathItem):
        self.odicts_widget.instances_view.model().add_odict(annotation_item.annotation_data.odict)

    def on_annotation_items_selected(self, item_numbers: list):
        # print(f"SlideViewerWidget.on_annotation_items_selected: {item_numbers}")
        # pass
        if item_numbers:
            self.odicts_widget.instances_view.select_odicts(item_numbers)
        else:
            self.odicts_widget.instances_view.clear_selection()

    def on_odicts_inserted(self, dict_numbers: list):
        for odict_number in dict_numbers:
            if odict_number >= len(self.view.annotation_items):
                odict = self.odicts_widget.instances_view.model().get_odict(odict_number)
                annotation_data = AnnotationData(odict)
                item = AnnotationPathItem(annotation_data, self.view.microns_per_pixel,
                                          self.view.get_current_view_scale())
                self.view.annotation_items.append(item)
                self.view.scene().addItem(item)

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
            odict = self.odicts_widget.instances_view.model().odicts[odict_number]
            if odict:
                # data = ordered_dict_to_data(odict)
                item: AnnotationPathItem = self.view.annotation_items[odict_number]
                item.annotation_data.odict = odict
                item.update()
                # update_item_by_data(item, data)

    def on_odicts_selected(self, dict_numbers: list):
        previous_selected_numbers = set(i for i, item in enumerate(self.view.annotation_items) if item.isSelected())
        new_selected_numbers = set(dict_numbers)
        # print(f"SlideViewerWidget.on_odicts_selected prev: {previous_selected_numbers}, new: {new_selected_numbers}")

        if previous_selected_numbers == new_selected_numbers:
            return

        item_numbers_to_select = new_selected_numbers - previous_selected_numbers
        items_to_select = [self.view.annotation_items[i] for i in item_numbers_to_select]
        # print(
        #     f"SlideViewerWidget.on_odicts_selected item_numbers_to_select: {item_numbers_to_select}, item_numbers_to_select: {items_to_select}")
        for item in items_to_select:
            item.setSelected(True)

        item_numbers_to_deselect = previous_selected_numbers - new_selected_numbers
        items_to_deselect = [self.view.annotation_items[i] for i in item_numbers_to_deselect]
        # print(
        #     f"SlideViewerWidget.item_numbers_to_deselect: {item_numbers_to_deselect}, items_to_deselect:{items_to_deselect}")
        for item in items_to_deselect:
            item.setSelected(False)

        items_bounding_rect = QRectF()
        selected_items = self.scene.selectedItems()
        for item in selected_items:
            item_rect = item.boundingRect().translated(item.pos().x(), item.pos().y())
            items_bounding_rect = items_bounding_rect.united(item_rect)
        if items_bounding_rect:
            self.view.fit_rect(items_bounding_rect)
