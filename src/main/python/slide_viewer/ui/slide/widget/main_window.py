import os
import typing
from collections import OrderedDict
from concurrent.futures import ThreadPoolExecutor
from typing import List

from PyQt5.QtCore import QSize, QSettings, Qt, QItemSelection, QItemSelectionModel, \
    QRectF, pyqtBoundSignal, QFileInfo, QFile, QPoint, QModelIndex
from PyQt5.QtGui import QCloseEvent, QColor, QBrush
from PyQt5.QtWidgets import QMainWindow, QApplication, QItemEditorFactory, \
    QDockWidget, QMdiArea, QMdiSubWindow, QMenu

from slide_viewer.common_qt.abcq_meta import ABCQMeta
from slide_viewer.common_qt.debounce_signal import debounce_one_arg_signal
from slide_viewer.common_qt.slot_disconnected import slot_disconnected
from slide_viewer.config import initial_main_window_size
from slide_viewer.ui.common.action.my_action import MyAction
from slide_viewer.ui.common.editor.custom_item_editor_factory import CustomItemEditorFactory
from slide_viewer.ui.model.filter.base_filter import FilterResults, FilterType
from slide_viewer.ui.model.filter.kmeans_filter import KMeansFilterData
from slide_viewer.ui.model.filter.nuclei import NucleiFilterData
from slide_viewer.ui.model.filter.threshold_filter import GrayManualThresholdFilterData
from slide_viewer.ui.odict.deep.base.deepable import toplevel_keys
from slide_viewer.ui.odict.deep.context_menu_factory2 import context_menu_factory2
from slide_viewer.ui.odict.deep.deepable_tree_model import DeepableTreeModel
from slide_viewer.ui.odict.deep.deepable_tree_view import DeepableTreeView
from slide_viewer.ui.odict.deep.model import AnnotationModel
from slide_viewer.ui.odict.filter_tree_view_delegate import FilterTreeViewDelegate
from slide_viewer.ui.slide.graphics.graphics_view import GraphicsView
from slide_viewer.ui.slide.widget.annotation_filter_processor import AnnotationFilterProcessor
from slide_viewer.ui.slide.widget.interface.active_annotation_tree_view_provider import ActiveAnnotationTreeViewProvider
from slide_viewer.ui.slide.widget.interface.active_view_provider import ActiveViewProvider
from slide_viewer.ui.slide.widget.interface.mdi_sub_window_service import SubWindowService, SyncOption
from slide_viewer.ui.slide.widget.mdi_sub_window import MdiSubWindow


class MainWindow(QMainWindow, ActiveViewProvider, ActiveAnnotationTreeViewProvider, SubWindowService,
                 metaclass=ABCQMeta):

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
        filters = OrderedDict({
            '1': GrayManualThresholdFilterData('1', (50, 100)),
            '2': KMeansFilterData('2'),
            '3': NucleiFilterData('3'),
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

            menu = QMenu()
            MyAction("Add filter", menu, on_add)

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

            def cleanup():
                view.setDisabled(True)
                # print(f'cleanup --------------')
                # print(f'cleanup {id(view)}')
                for sub_view in sub_views_except_active:
                    if sync_states.get(SyncOption.view_transform):
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
                        view.scene().annotationModelAdded.disconnect(sub_view.scene().add_annotation)
                        view.scene().annotationModelChanged.disconnect(sub_view.scene().edit_with_copy)
                        view.scene().annotationModelsRemoved.disconnect(sub_view.scene().remove_annotations)
                        view.scene().annotationModelsSelected.disconnect(sub_view.scene().select_annotations)

            for sub_view in sub_views_except_active:
                if sync_states.get(SyncOption.view_transform):
                    view.transformChanged.connect(sub_view.setTransform)
                    view.viewUpdated.connect(sub_view.update)
                    view.viewSceneRectUpdated.connect(sub_view.updateSceneRect)
                    view.viewSceneRectsUpdated.connect(sub_view.updateScene)
                if sync_states.get(SyncOption.grid_visible):
                    view.gridVisibleChanged.connect(sub_view.set_grid_visible)
                if sync_states.get(SyncOption.grid_size):
                    view.gridSizeChanged.connect(sub_view.set_grid_size)
                if sync_states.get(SyncOption.file_path):
                    view.filePathChanged.connect(sub_view.set_file_path)
                if sync_states.get(SyncOption.background_brush):
                    view.backgroundBrushChanged.connect(sub_view.set_background_brush)
                if sync_states.get(SyncOption.annotations):
                    view.scene().annotationModelAdded.connect(sub_view.scene().add_annotation)
                    view.scene().annotationModelChanged.connect(sub_view.scene().edit_with_copy)
                    view.scene().annotationModelsRemoved.connect(sub_view.scene().remove_annotations)
                    view.scene().annotationModelsSelected.connect(sub_view.scene().select_annotations)

            view.setDisabled(False)
            self.cleanup = cleanup

    def add_sub_window(self) -> MdiSubWindow:
        # It is important to update tree model from main gui thread and not from thread-pool task thread
        # It is important to update data of model only through model interface
        # We copy annotation, edit it and finally change model through model interface
        def on_filter_results_change(annotation_id: str, filter_results: FilterResults):
            model = typing.cast(AnnotationModel, annotations_tree_view.model()[annotation_id]).copy(deep=True)
            if filter_results.filter_type in (FilterType.KMEANS, FilterType.THRESHOLD):
                filter_results_attr = 'filter_results.normed_hist'
                model.filter_results = OrderedDict({'normed_hist': filter_results.metadata['normed_hist']})
                if filter_results_attr not in model.text_graphics_view_config.display_attrs:
                    model.text_graphics_view_config.display_attrs = model.text_graphics_view_config.display_attrs or []
                    model.text_graphics_view_config.display_attrs.append(filter_results_attr)
                annotations_tree_view.model()[annotation_id] = model
            elif filter_results.filter_type == FilterType.NUCLEI:
                filter_results_attr = 'filter_results.nuclei_count_str'
                nuclei_count_str = f"nuclei count: {filter_results.metadata['nuclei_count']}"
                model.filter_results = OrderedDict({'nuclei_count_str': nuclei_count_str})
                if filter_results_attr not in model.text_graphics_view_config.display_attrs:
                    model.text_graphics_view_config.display_attrs = model.text_graphics_view_config.display_attrs or []
                    model.text_graphics_view_config.display_attrs.append(filter_results_attr)
                annotations_tree_view.model()[annotation_id] = model

        slide_path_provider = lambda: view.slide_helper.slide_path
        annotation_model_provider = lambda annotation_id: annotations_tree_view.model()[annotation_id]
        filter_model_provider = lambda filter_id: self.filters_tree_view.model()[filter_id]
        annotation_filter_processor = AnnotationFilterProcessor(pool=self.pool,
                                                                slide_path_provider=slide_path_provider,
                                                                annotation_model_provider=annotation_model_provider,
                                                                filter_model_provider=filter_model_provider)
        annotation_filter_processor.filterResultsChange.connect(on_filter_results_change)
        view = GraphicsView(pixmap_provider=annotation_filter_processor, parent_=self)
        view.set_background_brush(QBrush(QColor("#A088BDBC")))
        view_sub_window = MdiSubWindow(self)
        view_sub_window.setWidget(view)
        self.view_mdi.addSubWindow(view_sub_window)

        model = DeepableTreeModel(_root=OrderedDict())
        annotations_tree_view = DeepableTreeView(self, model_=model)
        annotations_tree_view.setContextMenuPolicy(Qt.CustomContextMenu)
        annotations_tree_view.customContextMenuRequested.connect(context_menu_factory2(annotations_tree_view))
        annotations_tree_sub_window = self.annotations_tree_mdi.addSubWindow(annotations_tree_view)
        annotations_tree_sub_window.show()

        def on_view_activated():
            annotations_tree_sub_window.setFocus()

        def on_annotations_tree_view_activated():
            view_sub_window.setFocus()

        view_sub_window.aboutToActivate.connect(on_view_activated)
        annotations_tree_sub_window.aboutToActivate.connect(on_annotations_tree_view_activated)

        def on_file_path_changed(file_path: str):
            file_name = QFileInfo(QFile(file_path)).baseName()
            annotations_tree_sub_window.setToolTip(file_path)
            annotations_tree_sub_window.setWindowTitle(file_name)

        view_sub_window.widget().filePathChanged.connect(on_file_path_changed)

        def scene_annotation_model_added(annotation_model: AnnotationModel):
            # annotation_model.filter_id = '1'
            with slot_disconnected(annotations_tree_view.model().objectsInserted, tree_annotation_models_inserted):
                annotations_tree_view.model()[annotation_model.id] = annotation_model

        def scene_annotation_model_changed(annotation_model: AnnotationModel):
            with slot_disconnected(annotations_tree_view.model().objectsChanged, tree_annotation_models_changed):
                annotations_tree_view.model()[annotation_model.id] = annotation_model

        def scene_annotation_models_removed(ids: typing.List[str]):
            with slot_disconnected(annotations_tree_view.model().objectsRemoved, tree_annotation_models_removed):
                for i in ids:
                    del annotations_tree_view.model()[i]

        def scene_annotation_models_selected(ids: typing.List[str]):
            with slot_disconnected(annotations_tree_view.objectsSelected, tree_annotation_models_selected):
                selection = QItemSelection()
                for i in ids:
                    index = annotations_tree_view.model().key_to_index(i)
                    selection.select(index, annotations_tree_view.model().key_to_index(i, 1))
                annotations_tree_view.selectionModel().select(selection,
                                                              QItemSelectionModel.ClearAndSelect | QItemSelectionModel.Rows)

        def tree_annotation_models_changed(keys: List[str]):
            for toplevel_key in toplevel_keys(keys):
                model = annotations_tree_view.model()[toplevel_key]
                view.scene().edit_annotation(model)
            view.filter_graphics_item.update()
            # view.scene().annotations[toplevel_key].update()

        def tree_annotation_models_inserted(keys: List[str]):
            selected_toplevel_keys = toplevel_keys(keys) & set(keys)
            with slot_disconnected(view.scene().annotationModelAdded, scene_annotation_model_added):
                for annotation_id in selected_toplevel_keys:
                    annotation_model: AnnotationModel = annotations_tree_view.model()[annotation_id]
                    view.scene().add_annotation(annotation_model)
            for annotation_id in toplevel_keys(keys) - selected_toplevel_keys:
                model = annotations_tree_view.model()[annotation_id]
                view.scene().edit_annotation(model)
                # view.scene().annotations[annotation_id].update()

        def tree_annotation_models_removed(keys: List[str]):
            selected_toplevel_keys = toplevel_keys(keys) & set(keys)
            with slot_disconnected(view.scene().annotationModelsRemoved, scene_annotation_models_removed):
                view.scene().remove_annotations(list(selected_toplevel_keys))
            for annotation_id in toplevel_keys(keys) - selected_toplevel_keys:
                model = annotations_tree_view.model()[annotation_id]
                view.scene().edit_annotation(model)
                # view.scene().annotations[annotation_id].update()

        def tree_annotation_models_selected(keys: List[str]):
            with slot_disconnected(view.scene().annotationModelsSelected, scene_annotation_models_selected):
                for annotation in view.scene().annotations.values():
                    annotation.setSelected(False)
                annotations_bounding_rect = QRectF()
                for toplevel_key in toplevel_keys(keys):
                    annotation = view.scene().annotations[toplevel_key]
                    annotation.setSelected(True)
                    annotation_bounding_rect = annotation.boundingRect().translated(annotation.pos())
                    annotations_bounding_rect = annotations_bounding_rect.united(annotation_bounding_rect)
                if annotations_bounding_rect:
                    view.fit_rect(annotations_bounding_rect)

        view.scene().annotationModelChanged.connect(debounce_one_arg_signal(0.3, scene_annotation_model_changed))
        view.scene().annotationModelAdded.connect(scene_annotation_model_added)
        view.scene().annotationModelsRemoved.connect(scene_annotation_models_removed)
        view.scene().annotationModelsSelected.connect(scene_annotation_models_selected)
        annotations_tree_view.model().objectsChanged.connect(tree_annotation_models_changed)
        annotations_tree_view.model().objectsInserted.connect(tree_annotation_models_inserted)
        annotations_tree_view.model().objectsRemoved.connect(tree_annotation_models_removed)
        annotations_tree_view.objectsSelected.connect(tree_annotation_models_selected)

        def tree_filter_models_changed(keys: List[str]):
            view.filter_graphics_item.update()

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
        settings = QSettings("dieyepy", "dieyepy")
        settings.beginGroup("MainWindow")
        settings.setValue("size", self.size())
        settings.setValue("pos", self.pos())
        # settings.setValue("background_color", self.view.backgroundBrush().color())
        settings.endGroup()

    def read_settings(self):
        settings = QSettings("dieyepy", "dieyepy")
        settings.beginGroup("MainWindow")
        self.resize(settings.value("size", QSize(*initial_main_window_size)))
        self.move(settings.value("pos", QApplication.desktop().screen().rect().center() - self.rect().center()))
        # self.view.setBackgroundBrush(
        #     settings.value("background_color", QColor(initial_scene_background_color)))
        settings.endGroup()

    def closeEvent(self, event: QCloseEvent) -> None:
        self.write_settings()
        # QItemEditorFactory.setDefaultFactory(self.system_default_factory)
        event.accept()
