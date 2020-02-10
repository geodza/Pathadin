import os
import typing
from collections import OrderedDict
from concurrent.futures import ThreadPoolExecutor
from typing import List

from PyQt5.QtCore import QSize, Qt, pyqtBoundSignal, QFileInfo, QFile, QPoint, QModelIndex, QRectF, pyqtSignal
from PyQt5.QtGui import QCloseEvent, QColor, QBrush
from PyQt5.QtWidgets import QMainWindow, QApplication, QItemEditorFactory, \
    QDockWidget, QMdiArea, QMdiSubWindow, QMenu

from img.filter.keras_model import KerasModelFilterData
from img.filter.kmeans_filter import KMeansFilterData
from img.filter.manual_threshold import GrayManualThresholdFilterData
from img.filter.nuclei import NucleiFilterData
from img.filter.positive_pixel_count import PositivePixelCountFilterData
from img.filter.skimage_threshold import SkimageMeanThresholdFilterData
from img.proc.keras_model import KerasModelParams
from slide_viewer.common_qt.abcq_meta import ABCQMeta
from slide_viewer.common_qt.persistent_settings.settings_utils import write_settings, read_settings
from slide_viewer.common_qt.slot_disconnected_utils import slot_disconnected
from slide_viewer.config import initial_main_window_size
from slide_viewer.ui.common.action.my_action import MyAction
from slide_viewer.ui.common.editor.custom_item_editor_factory import CustomItemEditorFactory
from slide_viewer.ui.odict.deep.base.deepable import toplevel_keys
from slide_viewer.ui.odict.deep.context_menu_factory2 import context_menu_factory2
from slide_viewer.ui.odict.deep.deepable_tree_model import DeepableTreeModel
from slide_viewer.ui.odict.deep.deepable_tree_view import DeepableTreeView
from slide_viewer.ui.odict.filter_tree_view_delegate import FilterTreeViewDelegate
from slide_viewer.ui.slide.graphics.view.graphics_view import GraphicsView
from slide_viewer.ui.slide.graphics.view.graphics_view_annotation_service import GraphicsViewAnnotationService
from slide_viewer.ui.slide.widget.annotation_filter_processor import AnnotationFilterProcessor
from slide_viewer.ui.slide.widget.annotation_stats_processor import AnnotationStatsProcessor
from slide_viewer.ui.slide.widget.deepable_annotation_service import DeepableAnnotationService
from slide_viewer.ui.slide.widget.graphics_view_mdi_sub_window import GraphicsViewMdiSubWindow
from slide_viewer.ui.slide.widget.interface.active_annotation_tree_view_provider import ActiveAnnotationTreeViewProvider
from slide_viewer.ui.slide.widget.interface.active_view_provider import ActiveViewProvider
from slide_viewer.ui.slide.widget.interface.mdi_sub_window_service import SubWindowService, SyncOption
from slide_viewer.ui.slide.widget.mdi_sub_window import MdiSubWindow


class MainWindow(QMainWindow, ActiveViewProvider, ActiveAnnotationTreeViewProvider, SubWindowService,
                 metaclass=ABCQMeta):
    __sub_window_slide_path_changed = pyqtSignal(str)

    def get_sync_state(self, option: SyncOption) -> bool:
        return bool(self.sync_states.get(option))

    def set_sync_state(self, option: SyncOption, sync: bool) -> None:
        self.sync_states[option] = sync
        self.isSyncChanged.emit(option)

    @property
    def sub_views(self) -> List[GraphicsView]:
        return [typing.cast(GraphicsView, w.widget()) for w in self.view_mdi.subWindowList()]

    @property
    def active_sub_window(self) -> QMdiSubWindow:
        return self.view_mdi.activeSubWindow()

    @property
    def has_sub_windows(self) -> bool:
        return self.view_mdi.activeSubWindow() is not None

    @property
    def sub_window_activated(self) -> pyqtBoundSignal:
        return self.view_mdi.subWindowActivated

    @property
    def sub_window_slide_path_changed(self) -> pyqtBoundSignal(str):
        return self.__sub_window_slide_path_changed

    def tile_sub_windows(self) -> None:
        self.view_mdi.tileSubWindows()

    @property
    def active_view(self) -> typing.Optional[GraphicsView]:
        active = self.view_mdi.activeSubWindow()
        return active.widget() if active else None

    @property
    def active_annotation_tree_view(self) -> typing.Optional[DeepableTreeView]:
        active = self.annotations_tree_mdi.activeSubWindow()
        return active.widget() if active else None

    def __init__(self):
        super().__init__()
        self.sync_states: typing.Dict[SyncOption, bool] = {}
        self.cleanup: typing.Optional[typing.Callable[[], None]] = None

        # fd = QuantizationFilterData('1')
        # fd = KMeansFilterData('1')
        # fd = NucleiFilterData('1')
        model_path1 = r"C:\Users\User\GoogleDisk\datasets\weights.h5"
        model_path2 = r"C:\Users\User\GoogleDisk\datasets\weights3.h5"
        model_path = None
        filters = OrderedDict({
            '1': GrayManualThresholdFilterData('1', (50, 100)),
            '2': KMeansFilterData('2'),
            '3': NucleiFilterData('3'),
            '4': SkimageMeanThresholdFilterData('4'),
            '5': PositivePixelCountFilterData('5'),
            '6': KerasModelFilterData('6', KerasModelParams(model_path)),
            # '7': KerasModelFilterData('7', KerasModelParams(model_path2)),
        })

        self.view_mdi = QMdiArea(self)
        self.setCentralWidget(self.view_mdi)
        # print(f"order {self.view_mdi.activationOrder()}")
        filters_model = DeepableTreeModel(_root=filters)
        self.filters_tree_view = DeepableTreeView(self, model_=filters_model)
        self.filters_tree_view.setContextMenuPolicy(Qt.CustomContextMenu)

        def on_filter_context_menu(position: QPoint):
            if not self.filters_tree_view.model().rowCount():
                return
            if not self.filters_tree_view.indexAt(position).isValid():
                self.filters_tree_view.setCurrentIndex(QModelIndex())

            def on_add():
                last_filted_id = len(self.filters_tree_view.model())
                new_filter_id = str(last_filted_id + 1)
                self.filters_tree_view.model()[new_filter_id] = GrayManualThresholdFilterData(new_filter_id)

            def on_reset():
                self.filters_tree_view.model().beginResetModel()
                self.filters_tree_view.model().endResetModel()


            menu = QMenu()
            MyAction("Add filter", menu, on_add)
            MyAction(f"Reset model", menu, on_reset)

            menu.exec_(self.filters_tree_view.viewport().mapToGlobal(position))

        self.filters_tree_view.customContextMenuRequested.connect(on_filter_context_menu)

        filters_delegate = FilterTreeViewDelegate(filters_model)
        self.filters_tree_view.setItemDelegate(filters_delegate)
        self.annotations_tree_mdi = QMdiArea(self)
        self.annotations_tree_mdi.setViewMode(QMdiArea.TabbedView)

        filters_dock_widget = QDockWidget('Filters', self)
        self.addDockWidget(Qt.RightDockWidgetArea, filters_dock_widget)
        filters_dock_widget.setWidget(self.filters_tree_view)
        filters_dock_widget.setFeatures(filters_dock_widget.features() & ~QDockWidget.DockWidgetClosable)

        annotations_dock_widget = QDockWidget('Annotations', self)
        self.addDockWidget(Qt.RightDockWidgetArea, annotations_dock_widget)
        annotations_dock_widget.setWidget(self.annotations_tree_mdi)
        annotations_dock_widget.setFeatures(annotations_dock_widget.features() & ~QDockWidget.DockWidgetClosable)

        self.resizeDocks([annotations_dock_widget, filters_dock_widget], [600, 600], Qt.Horizontal)
        self.resizeDocks([annotations_dock_widget, filters_dock_widget], [500, 500], Qt.Vertical)

        # self.setup_editor_factory()
        self.view_mdi.subWindowActivated.connect(self.on_init_sync)
        self.isSyncChanged.connect(self.on_init_sync)

        # self.read_settings()
        max_workers = os.cpu_count()
        max_workers = max_workers - 1 if max_workers > 1 else max_workers
        self.pool = ThreadPoolExecutor(max_workers, thread_name_prefix="main_window_")
        self.pending = set()

    def __del__(self):
        self.pool.shutdown(False)

    def on_init_sync(self):
        if self.cleanup:
            self.cleanup()
            self.cleanup = None
        view = self.active_view
        if view:
            sub_views_except_active = [sw for sw in self.sub_views if sw is not view]
            sync_states = dict(self.sync_states)

            # print(f"active view: {view.id}")

            def cleanup():
                view.setDisabled(True)
                # print(f'cleanup --------------')
                # print(f'cleanup {id(view)}')
                for sub_view in sub_views_except_active:
                    if sync_states.get(SyncOption.view_transform):
                        # pass
                        view.transformChanged.disconnect(sub_view.setTransform)
                        view.viewUpdated.disconnect(sub_view.update)
                        view.viewSceneRectUpdated.disconnect(sub_view.updateSceneRect)
                        view.viewSceneRectsUpdated.disconnect(sub_view.updateScene)
                    if sync_states.get(SyncOption.grid_visible):
                        view.gridVisibleChanged.disconnect(sub_view.set_grid_visible)
                    if sync_states.get(SyncOption.grid_size):
                        view.gridSizeChanged.disconnect(sub_view.set_grid_size)
                    if sync_states.get(SyncOption.file_path):
                        view.filePathChanged.disconnect(sub_view.set_file_path)
                    if sync_states.get(SyncOption.background_brush):
                        view.backgroundBrushChanged.disconnect(sub_view.set_background_brush)
                    if sync_states.get(SyncOption.annotations):
                        view.annotation_service.added_signal().disconnect(sub_view.annotation_service.add_copy)
                        view.annotation_service.deleted_signal().disconnect(sub_view.annotation_service.delete_if_exist)
                        view.scene().annotationModelsSelected.disconnect(sub_view.scene().select_annotations)
                        # try:
                        if sync_states.get(SyncOption.annotation_filter):
                            view.annotation_service.edited_signal().disconnect(sub_view.annotation_service.add_or_edit_with_copy)
                        else:
                            view.annotation_service.edited_signal().disconnect(sub_view.annotation_service.add_or_edit_with_copy_without_filter)
                        # except:
                        #     pass

            for sub_view in sub_views_except_active:
                if sync_states.get(SyncOption.view_transform):
                    # pass
                    view.transformChanged.connect(sub_view.setTransform)
                    view.viewUpdated.connect(sub_view.update)
                    view.viewSceneRectUpdated.connect(sub_view.updateSceneRect)
                    view.viewSceneRectsUpdated.connect(sub_view.updateScene)
                if sync_states.get(SyncOption.grid_visible):
                    view.gridVisibleChanged.connect(sub_view.set_grid_visible)
                if sync_states.get(SyncOption.grid_size):
                    view.gridSizeChanged.connect(sub_view.set_grid_size)
                if sync_states.get(SyncOption.file_path):
                    # view.filePathChanged.connect(sub_view.set_file_path)
                    view.filePathChanged.connect(sub_view.set_file_path)
                if sync_states.get(SyncOption.background_brush):
                    view.backgroundBrushChanged.connect(sub_view.set_background_brush)
                if sync_states.get(SyncOption.annotations):
                    # view.annotation_service.added_signal().connect(sub_view.annotation_service.add_copy, type=Qt.QueuedConnection)
                    view.annotation_service.added_signal().connect(sub_view.annotation_service.add_copy)
                    view.annotation_service.deleted_signal().connect(sub_view.annotation_service.delete_if_exist)
                    view.scene().annotationModelsSelected.connect(sub_view.scene().select_annotations)
                    if sync_states.get(SyncOption.annotation_filter):
                        # view.annotation_service.edited_signal().connect(sub_view.annotation_service.add_or_edit_with_copy, type=Qt.QueuedConnection)
                        view.annotation_service.edited_signal().connect(sub_view.annotation_service.add_or_edit_with_copy)
                        # view.annotation_service.edited_signal().connect(debounce_slot(0.01, sub_view.annotation_service.add_or_edit_with_copy))
                    else:
                        view.annotation_service.edited_signal().connect(sub_view.annotation_service.add_or_edit_with_copy_without_filter)

            view.setDisabled(False)
            self.cleanup = cleanup

        self.read_settings()

    def add_sub_window(self) -> GraphicsViewMdiSubWindow:
        annotations_tree_model = DeepableTreeModel(_root=OrderedDict())
        annotations_tree_view = DeepableTreeView(self, model_=annotations_tree_model)
        annotations_tree_view.setContextMenuPolicy(Qt.CustomContextMenu)
        annotations_tree_view.customContextMenuRequested.connect(context_menu_factory2(annotations_tree_view))
        annotation_tree_view_sub_window = MdiSubWindow(self)
        annotation_tree_view_sub_window.setWidget(annotations_tree_view)
        annotations_tree_sub_window = self.annotations_tree_mdi.addSubWindow(annotation_tree_view_sub_window)
        annotations_tree_sub_window.show()

        annotation_service = DeepableAnnotationService(root=annotations_tree_model)
        slide_path_provider = lambda: view.slide_helper.slide_path
        filter_model_provider = lambda filter_id: self.filters_tree_view.model()[filter_id]
        scene_provider = lambda: view.scene()
        annotation_filter_processor = AnnotationFilterProcessor(pool=self.pool,
                                                                slide_path_provider=slide_path_provider,
                                                                annotation_service=annotation_service,
                                                                filter_model_provider=filter_model_provider)
        annotation_stats_processor = AnnotationStatsProcessor(slide_stats_provider=None)
        graphics_view_annotation_service = GraphicsViewAnnotationService(scene_provider=scene_provider,
                                                                         annotation_service=annotation_service,
                                                                         annotation_pixmap_provider=annotation_filter_processor,
                                                                         annotation_stats_processor=annotation_stats_processor,
                                                                         scale_provider=None,
                                                                         slide_stats_provider=None)
        view = GraphicsView(parent_=self, graphics_view_annotation_service=graphics_view_annotation_service)
        annotation_stats_processor.slide_stats_provider = view
        graphics_view_annotation_service.slide_stats_provider = view
        graphics_view_annotation_service.scale_provider = view
        view.set_background_brush(QBrush(QColor("#A088BDBC")))
        view_sub_window = GraphicsViewMdiSubWindow(self)
        view_sub_window.setWidget(view)
        self.view_mdi.addSubWindow(view_sub_window)

        def on_view_activated():
            annotations_tree_sub_window.setFocus()

        def on_annotations_tree_view_activated():
            view_sub_window.setFocus()

        def on_close_view_sub_window():
            annotation_tree_view_sub_window.close()

        def on_close_annotations_tree_view():
            view_sub_window.close()

        def on_file_path_changed(file_path: str):
            file_name = QFileInfo(QFile(file_path)).baseName()
            annotations_tree_sub_window.setToolTip(file_path)
            annotations_tree_sub_window.setWindowTitle(file_name)
            # self.sub_window_slide_path_changed.emit(file_path)
            # annotations_tree_sub_window.activateWindow()
            # view_sub_window.activateWindow()
            # self.sub_window_activated.emit(view_sub_window)
            # if view_sub_window.isActiveWindow():
            #     self.sub_window_activated.emit(view_sub_window)

        def on_file_path_dropped(file_path: str):
            self.sub_window_activated.emit(view_sub_window)

        def on_scene_annotations_selected(ids: typing.List[str]):
            with slot_disconnected(annotations_tree_view.objectsSelected, on_tree_objects_selected):
                annotations_tree_view.select_keys(ids)

        def on_tree_objects_selected(keys: typing.List[str]):
            with slot_disconnected(view.scene().annotationModelsSelected, on_scene_annotations_selected):
                ids = toplevel_keys(keys) & set(keys)
                annotations_bounding_rect = QRectF()
                for id_, annotation in view.scene().annotations.items():
                    if id_ in ids:
                        annotation.setSelected(True)
                        annotation_bounding_rect = annotation.boundingRect().translated(annotation.pos())
                        annotations_bounding_rect = annotations_bounding_rect.united(annotation_bounding_rect)
                    else:
                        annotation.setSelected(False)
                if annotations_bounding_rect:
                    view.fit_rect(annotations_bounding_rect)

        def tree_filter_models_changed(keys: List[str]):
            if view and view.filter_graphics_item:
                view.filter_graphics_item.update()

        view_sub_window.aboutToActivate.connect(on_view_activated)
        annotations_tree_sub_window.aboutToActivate.connect(on_annotations_tree_view_activated)
        view_sub_window.aboutToClose.connect(on_close_view_sub_window)
        annotations_tree_sub_window.aboutToClose.connect(on_close_annotations_tree_view)
        view_sub_window.widget().filePathChanged.connect(on_file_path_changed)
        view_sub_window.widget().filePathDropped.connect(on_file_path_dropped)
        view.scene().annotationModelsSelected.connect(on_scene_annotations_selected)
        annotations_tree_view.objectsSelected.connect(on_tree_objects_selected)
        self.filters_tree_view.model().objectsChanged.connect(tree_filter_models_changed)

        return view_sub_window

    def setup_editor_factory(self):
        self.system_default_factory = QItemEditorFactory.defaultFactory()
        # editor_factory = QItemEditorFactory()
        editor_factory = CustomItemEditorFactory(self.system_default_factory)
        # editor_factory = QItemEditorFactory.defaultFactory()
        # editor_factory.registerEditor(QVariant.Color, ColorEditorCreatorBase(self.ctx.icon_palette))
        QItemEditorFactory.setDefaultFactory(editor_factory)

    def write_settings(self):
        settings = {
            "size": self.size(),
            "pos": self.pos()
        }
        write_settings("dieyepy", "MainWindow", settings)
        # settings.setValue("background_color", self.view.backgroundBrush().color())

    def read_settings(self):
        settings = read_settings("dieyepy", "MainWindow")
        self.resize(settings.get("size", QSize(*initial_main_window_size)))
        self.move(settings.get("pos", QApplication.desktop().screen().rect().center() - self.rect().center()))
        # self.view.setBackgroundBrush(
        #     settings.value("background_color", QColor(initial_scene_background_color)))

    def closeEvent(self, event: QCloseEvent) -> None:
        self.write_settings()
        # QItemEditorFactory.setDefaultFactory(self.system_default_factory)
        event.accept()