import os
import typing
from collections import OrderedDict
from concurrent.futures import ThreadPoolExecutor
from typing import List

from PyQt5.QtCore import QSize, Qt, pyqtBoundSignal, QFileInfo, QFile, QRectF, pyqtSignal
from PyQt5.QtGui import QCloseEvent, QColor, QBrush
from PyQt5.QtWidgets import QMainWindow, QApplication, QItemEditorFactory, \
	QDockWidget, QMdiArea, QMdiSubWindow

from common_qt.abcq_meta import ABCQMeta
from common_qt.editor.custom_item_editor_factory import CustomItemEditorFactory
from common_qt.mdi_subwindow_sync_utils import sync_about_to_activate, sync_close
from common_qt.persistent_settings.settings_utils import write_settings, read_settings
from common_qt.slot_disconnected_utils import slot_disconnected
from deepable.core import toplevel_keys
from deepable_qt.tree_view_config_deepable_tree_model import TreeViewConfigDeepableTreeModel
from deepable_qt.deepable_tree_view import DeepableTreeView
from img.filter.base_filter import FilterData
from img.filter.keras_model import KerasModelFilterData, KerasModelParams
from img.filter.kmeans_filter import KMeansFilterData
from img.filter.manual_threshold import GrayManualThresholdFilterData, HSVManualThresholdFilterData
from img.filter.nuclei import NucleiFilterData
from img.filter.positive_pixel_count import PositivePixelCountFilterData
from img.filter.skimage_threshold import SkimageMeanThresholdFilterData
from slide_viewer.config import initial_main_window_size, model_path
from slide_viewer.ui.slide.widget.annotation.annotations_tree_view import create_annotations_tree_view
from slide_viewer.ui.slide.widget.filter.filter_tree_view_delegate import FilterTreeViewDelegate
from slide_viewer.ui.common.model import AnnotationModel
from slide_viewer.ui.slide.graphics.view.graphics_view import GraphicsView
from slide_viewer.ui.slide.graphics.view.graphics_view_annotation_service2 import GraphicsViewAnnotationService2
from slide_viewer.ui.slide.widget.annotation_filter_processor import AnnotationFilterProcessor
from slide_viewer.ui.slide.widget.annotation_stats_processor import AnnotationStatsProcessor
from slide_viewer.ui.slide.widget.deepable_annotation_service import DeepableAnnotationService
from slide_viewer.ui.slide.widget.filter.filters_tree_view import create_filters_tree_view, \
	create_filters_tree_view_context_menu
from slide_viewer.ui.slide.widget.graphics_view_mdi_sub_window import GraphicsViewMdiSubWindow
from slide_viewer.ui.slide.widget.interface.active_annotation_tree_view_provider import ActiveAnnotationTreeViewProvider
from slide_viewer.ui.slide.widget.interface.active_view_provider import ActiveViewProvider
from slide_viewer.ui.slide.widget.interface.mdi_sub_window_service import SubWindowService, SyncOption
from slide_viewer.ui.slide.widget.main_window_view_sync import setup_sync
from slide_viewer.ui.slide.widget.mdi_sub_window import MdiSubWindow
from slide_viewer.ui.slide.widget.menubar import Menubar


class MainWindow(QMainWindow, ActiveViewProvider, ActiveAnnotationTreeViewProvider, SubWindowService,
				 metaclass=ABCQMeta):
	__sub_window_slide_path_changed = pyqtSignal(str)

	def menuBar(self) -> Menubar:
		return typing.cast(Menubar, super().menuBar())

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

		filters = OrderedDict({
			'GRAY': GrayManualThresholdFilterData('GRAY', True, (150, 100)),
			'HSV': HSVManualThresholdFilterData('HSV', True, ((165, 40, 0), (15, 255, 255))),
			'KMEANS': KMeansFilterData('KMEANS'),
			'NUCLEI': NucleiFilterData('NUCLEI'),
			'SKIMAGE_MEAN': SkimageMeanThresholdFilterData('SKIMAGE_MEAN'),
			'PIXEL_COUNT': PositivePixelCountFilterData('PIXEL_COUNT'),
			'KERAS': KerasModelFilterData('KERAS', True, KerasModelParams(model_path)),
			# '7': KerasModelFilterData('7', KerasModelParams(model_path2)),
		})

		self.view_mdi = QMdiArea(self)
		self.setCentralWidget(self.view_mdi)
		# print(f"order {self.view_mdi.activationOrder()}")

		filters_model = TreeViewConfigDeepableTreeModel(_root=filters)
		# filters_model = TreeViewConfigDeepableTreeModel()
		self.filters_tree_view = create_filters_tree_view(self, filters_model)
		filters_dock_widget = QDockWidget('Filters', self)
		filters_dock_widget.setWidget(self.filters_tree_view)
		filters_dock_widget.setFeatures(filters_dock_widget.features() & ~QDockWidget.DockWidgetClosable)
		self.addDockWidget(Qt.RightDockWidgetArea, filters_dock_widget)

		self.annotations_tree_mdi = QMdiArea(self)
		self.annotations_tree_mdi.setViewMode(QMdiArea.TabbedView)
		annotations_dock_widget = QDockWidget('Annotations', self)
		annotations_dock_widget.setWidget(self.annotations_tree_mdi)
		annotations_dock_widget.setFeatures(annotations_dock_widget.features() & ~QDockWidget.DockWidgetClosable)
		self.addDockWidget(Qt.RightDockWidgetArea, annotations_dock_widget)

		self.resizeDocks([annotations_dock_widget, filters_dock_widget], [600, 600], Qt.Horizontal)
		self.resizeDocks([annotations_dock_widget, filters_dock_widget], [500, 500], Qt.Vertical)

		# self.setup_editor_factory()

		# def on_activated(w):
		#     print("on_activated", w)

		# self.view_mdi.subWindowActivated.connect(on_activated)
		self.view_mdi.subWindowActivated.connect(self.on_init_sync)
		self.isSyncChanged.connect(self.on_init_sync)

		max_workers = os.cpu_count()
		max_workers = max_workers - 1 if max_workers > 1 else max_workers
		self.pool = ThreadPoolExecutor(max_workers, thread_name_prefix="main_window_")
		self.read_settings()

	def __del__(self):
		self.pool.shutdown(False)

	def on_init_sync(self, except_view: GraphicsView):
		if self.cleanup:
			self.cleanup()
			self.cleanup = None
		if self.active_view:
			view = self.active_view
			sub_views_except_active = [sw for sw in self.sub_views if sw is not view and sw is not except_view]
			sync_states = dict(self.sync_states)
			# print(f"active view: {view.id}")
			self.cleanup = setup_sync(view, sub_views_except_active, sync_states)

	def add_sub_window(self) -> GraphicsViewMdiSubWindow:
		annotations_tree_model = TreeViewConfigDeepableTreeModel(_root=OrderedDict())
		annotations_tree_view = create_annotations_tree_view(self, annotations_tree_model)
		annotation_tree_view_sub_window = MdiSubWindow(self)
		annotation_tree_view_sub_window.setWidget(annotations_tree_view)
		annotations_tree_sub_window = self.annotations_tree_mdi.addSubWindow(annotation_tree_view_sub_window)
		annotations_tree_sub_window.show()

		microns_per_pixel_provider = lambda: view.get_microns_per_pixel()
		annotation_stats_processor = AnnotationStatsProcessor(microns_per_pixel_provider=microns_per_pixel_provider)
		annotation_service = DeepableAnnotationService(root=annotations_tree_model,
													   stats_processor=annotation_stats_processor)
		slide_path_provider = lambda: view.slide_helper.slide_path

		def filter_model_provider(filter_id: str):
			if filter_id in self.filters_tree_view.model():
				for key in self.filters_tree_view.model():
					fd: FilterData = self.filters_tree_view.model()[key]
					if fd.id == filter_id:
						return fd
			# return self.filters_tree_view.model()[filter_id]
			else:
				return None

		scene_provider = lambda: view.scene()

		# annotation_filter_processor = None
		annotation_filter_processor = AnnotationFilterProcessor(pool=self.pool,
																slide_path_provider=slide_path_provider,
																annotation_service=annotation_service,
																filter_model_provider=filter_model_provider)
		graphics_view_annotation_service = GraphicsViewAnnotationService2(scene_provider=scene_provider,
																		  annotation_service=annotation_service,
																		  scale_provider=None)

		view = GraphicsView(parent_=self,
							graphics_view_annotation_service=graphics_view_annotation_service,
							annotation_pixmap_provider=annotation_filter_processor)
		graphics_view_annotation_service.slide_stats_provider = view
		graphics_view_annotation_service.scale_provider = view
		view.set_background_brush(QBrush(QColor("#A088BDBC")))
		view_sub_window = GraphicsViewMdiSubWindow(self)
		view_sub_window.setWidget(view)
		self.view_mdi.addSubWindow(view_sub_window)

		def on_file_path_changed(file_path: str):
			file_name = QFileInfo(QFile(file_path)).baseName()
			annotations_tree_sub_window.setToolTip(file_path)
			annotations_tree_sub_window.setWindowTitle(file_name)

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

		def on_about_to_close():
			print("on_about_to_close", view_sub_window)
			self.on_init_sync(view)

		sync_about_to_activate(view_sub_window, annotation_tree_view_sub_window)
		sync_close(view_sub_window, annotation_tree_view_sub_window)
		view_sub_window.aboutToClose.connect(on_about_to_close)
		view.filePathChanged.connect(on_file_path_changed)
		view.filePathDropped.connect(on_file_path_dropped)
		view.scene().annotationModelsSelected.connect(on_scene_annotations_selected)
		annotations_tree_view.objectsSelected.connect(on_tree_objects_selected)
		self.filters_tree_view.model().keysChanged.connect(tree_filter_models_changed)

		def on_annotation_model_edited(id_: str, model: AnnotationModel):
			with slot_disconnected(annotation_service.edited_signal(), on_annotation_model_edited):
				stats = annotation_stats_processor.calc_stats(model)
				annotation_service.edit_stats(id_, stats)

		annotation_service.edited_signal().connect(on_annotation_model_edited)

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
		write_settings("pathadin", "MainWindow", settings)

	# settings.setValue("background_color", self.view.backgroundBrush().color())

	def read_settings(self):
		settings = read_settings("pathadin", "MainWindow")
		self.resize(settings.get("size", QSize(*initial_main_window_size)))
		self.move(settings.get("pos", QApplication.desktop().screen().rect().center() - self.rect().center()))

	# self.view.setBackgroundBrush(
	#     settings.value("background_color", QColor(initial_scene_background_color)))

	def closeEvent(self, event: QCloseEvent) -> None:
		self.write_settings()
		# QItemEditorFactory.setDefaultFactory(self.system_default_factory)
		event.accept()
