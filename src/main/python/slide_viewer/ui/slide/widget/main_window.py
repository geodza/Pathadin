import os
import typing
from collections import OrderedDict
from concurrent.futures import ThreadPoolExecutor
from typing import List

from PyQt5.QtCore import QSize, Qt, pyqtBoundSignal, QFileInfo, QFile
from PyQt5.QtGui import QCloseEvent, QColor, QBrush
from PyQt5.QtWidgets import QMainWindow, QApplication, QDockWidget, QMdiArea, QMdiSubWindow

from common_qt.abcq_meta import ABCQMeta
from common_qt.core import QMdiAreaP, QDockWidgetP
from common_qt.mvc.view.delegate.abstract_item_view_delegate import AbstractItemViewDelegate
from common_qt.mvc.view.delegate.styled_item_view_delegate import QStyledItemViewDelegate
from common_qt.persistent_settings.settings_utils import write_settings, read_settings
from common_qt.util.mdi_subwindow_sync_utils import sync_about_to_activate, sync_close
from deepable_qt.model.deepable_tree_model import DeepableTreeModel
from deepable_qt.model.tree_view_config_deepable_tree_model_delegate import TreeViewConfigDeepableTreeModelDelegate
from deepable_qt.view.deepable_tree_view import DeepableTreeView
from filter.filter_plugin import FilterPlugin
from filter.keras.keras_model_filter_model import KerasModelFilterData, KerasModelParams
from filter.kmeans.kmeans_filter_model import KMeansFilterData
from filter.manual_threshold.manual_threshold_filter_model import GrayManualThresholdFilterData, \
	HSVManualThresholdFilterData
from filter.nuclei.nuclei_filter_model import NucleiFilterData
from filter.positive_pixel_count.positive_pixel_count_filter_model import PositivePixelCountFilterData
from filter.skimage_threshold.skimage_threshold_filter_model import SkimageMeanThresholdFilterData
from slide_viewer.config import initial_main_window_size, model_path
from slide_viewer.ui.slide.graphics.view.graphics_view import GraphicsView
from slide_viewer.ui.slide.graphics.view.graphics_view_annotation_service3 import GraphicsViewAnnotationService3
from slide_viewer.ui.slide.widget.annotation.annotation_filter_processor import AnnotationFilterProcessor
from slide_viewer.ui.slide.widget.annotation.annotation_service import AnnotationService
from slide_viewer.ui.slide.widget.annotation.annotations_tree_view import create_annotations_tree_view
from slide_viewer.ui.slide.widget.annotation.deepable_annotation_service import DeepableAnnotationService
from slide_viewer.ui.slide.widget.filter.filter_data_service import FilterDataService
from slide_viewer.ui.slide.widget.filter.filters_tree_view import create_filters_tree_view, create_filters_tree_model, \
	create_filter_processor
from slide_viewer.ui.slide.widget.filtered_annotation_model_delegate import FilterAnnotationViewDelegate
from slide_viewer.ui.slide.widget.graphics_view_mdi_sub_window import GraphicsViewMdiSubWindow
from slide_viewer.ui.slide.widget.interface.active_annotation_service_provider import ActiveAnnotationServiceProvider
from slide_viewer.ui.slide.widget.interface.active_annotation_tree_view_provider import ActiveAnnotationTreeViewProvider
from slide_viewer.ui.slide.widget.interface.active_view_provider import ActiveViewProvider
from slide_viewer.ui.slide.widget.interface.mdi_sub_window_service import SubWindowService
from slide_viewer.ui.slide.widget.mdi_sub_window import MdiSubWindow
from slide_viewer.ui.slide.widget.sync.annotation_stats import sync_annotations_stats
from slide_viewer.ui.slide.widget.sync.annotations import sync_graphics_and_model_annotations, \
	sync_filtered_annotation_graphics_item_and_model_annotations
from slide_viewer.ui.slide.widget.sync.filters import sync_graphics_and_model_filters
from slide_viewer.ui.slide.widget.sync.selection import sync_graphics_and_model_selection
from slide_viewer.ui.slide.widget.sync.sub_window.annotation_services_synchronizer import \
	AnnotationServicesSynchronizer, \
	AnnotationServiceSyncOptions
from slide_viewer.ui.slide.widget.sync.sub_window.graphics_views_synchronizer import GraphicsViewsSynchronizer, \
	GraphicsViewSyncOptions
from slide_viewer.ui.slide.widget.sync.sync_option import SyncOption


class MainWindow(QMainWindow, ActiveViewProvider, ActiveAnnotationTreeViewProvider, ActiveAnnotationServiceProvider,
				 SubWindowService,
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
	def sub_services(self) -> List[AnnotationService]:
		return [typing.cast(AnnotationService, w.annotation_service) for w in
				self.annotations_tree_mdi.subWindowList()]

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

	@property
	def active_annotation_service(self) -> typing.Optional[AnnotationService]:
		active = self.annotations_tree_mdi.activeSubWindow()
		return active.annotation_service if active else None

	def __init__(self, filter_plugins: List[FilterPlugin] = []):
		super().__init__()
		self.filter_plugins = filter_plugins
		self.sync_states: typing.Dict[SyncOption, bool] = {}
		self.graphics_views_cleanup: typing.Optional[typing.Callable[[], None]] = None
		self.tree_models_cleanup: typing.Optional[typing.Callable[[], None]] = None

		self.graphics_views_synchronizer = GraphicsViewsSynchronizer()
		self.annotation_services_synchronizer = AnnotationServicesSynchronizer()

		filters = [
			GrayManualThresholdFilterData('G', 'Gray', gray_range=(150, 100)),
			HSVManualThresholdFilterData('H', 'HSV', hsv_range=((165, 40, 0), (15, 255, 255))),
			KMeansFilterData('K', 'KMeans'),
			NucleiFilterData('N', 'Nuclei'),
			SkimageMeanThresholdFilterData('S', 'SkimageMean'),
			PositivePixelCountFilterData('P', 'PPC'),
			KerasModelFilterData('E', 'KerasModel', keras_model_params=KerasModelParams(model_path)),
			KerasModelFilterData('EM', 'KerasModel_multi_class',
								 keras_model_params=KerasModelParams(model_path, cmap='viridis')),
			KerasModelFilterData('EMZ', 'KerasModel_multi_class_zoom_5',
								 keras_model_params=KerasModelParams(model_path, alpha_scale=0.8, patch_size_scale=4.0,
																	 cmap='viridis')),
		]

		self.view_mdi = QMdiArea(self)
		self.setCentralWidget(self.view_mdi)
		# print(f"order {self.view_mdi.activationOrder()}")

		# model_delegate = TreeViewConfigDeepableTreeModelDelegate()
		filters_model = create_filters_tree_model(filters)
		self.filter_data_service = FilterDataService(filters_model)
		# filters_model = TreeViewConfigDeepableTreeModel()
		self.filters_tree_view = create_filters_tree_view(self, filters_model, self.filter_plugins)
		filters_dock_widget = QDockWidgetP('Filters', self, widget=self.filters_tree_view,
										   features=QDockWidget.DockWidgetMovable | QDockWidget.DockWidgetFloatable)
		self.addDockWidget(Qt.RightDockWidgetArea, filters_dock_widget)

		self.annotations_tree_mdi = QMdiAreaP(self, view_mode=QMdiArea.TabbedView)
		annotations_dock_widget = QDockWidgetP('Annotations', self, widget=self.annotations_tree_mdi,
											   features=QDockWidget.DockWidgetMovable | QDockWidget.DockWidgetFloatable)
		self.addDockWidget(Qt.RightDockWidgetArea, annotations_dock_widget)

		self.resizeDocks([annotations_dock_widget, filters_dock_widget], [600, 600], Qt.Horizontal)
		self.resizeDocks([annotations_dock_widget, filters_dock_widget], [500, 500], Qt.Vertical)

		# def on_activated(w):
		#     print("on_activated", w)

		# self.view_mdi.subWindowActivated.connect(on_activated)

		self.view_mdi.subWindowActivated.connect(self.sync_graphics_views)
		self.isSyncChanged.connect(self.sync_graphics_views)

		self.annotations_tree_mdi.subWindowActivated.connect(self.sync_tree_models)
		self.isSyncChanged.connect(self.sync_tree_models)

		max_workers = os.cpu_count()
		max_workers = max_workers - 1 if max_workers > 1 else max_workers
		max_workers = min(7, max_workers - 1 if max_workers > 1 else max_workers)
		self.pool = ThreadPoolExecutor(max_workers, thread_name_prefix="main_window_")
		self.read_settings()

	def __del__(self):
		self.pool.shutdown(False)

	def sync_graphics_views(self, option: SyncOption):
		options = GraphicsViewSyncOptions(self.sync_states.get(SyncOption.view_transform, False),
										  self.sync_states.get(SyncOption.grid_visible, False),
										  self.sync_states.get(SyncOption.grid_size, False),
										  self.sync_states.get(SyncOption.file_path, False),
										  self.sync_states.get(SyncOption.background_brush, False),
										  self.sync_states.get(SyncOption.annotations, False))
		self.graphics_views_synchronizer.sync(self.active_view, self.sub_views, options)

	def sync_tree_models(self, option: SyncOption):
		options = AnnotationServiceSyncOptions(self.sync_states.get(SyncOption.annotations, False),
											   self.sync_states.get(SyncOption.annotation_filter, False))
		self.annotation_services_synchronizer.sync(self.active_annotation_service, self.sub_services, options)

	def add_sub_window(self) -> GraphicsViewMdiSubWindow:
		# annotations_tree_model_delegate = FilteredAnnotationModelDelegate(TreeViewConfigDeepableTreeModelDelegate(),None)
		annotations_tree_model_delegate = TreeViewConfigDeepableTreeModelDelegate()
		annotations_tree_model = DeepableTreeModel(_root=OrderedDict(),
												   _modelDelegate=annotations_tree_model_delegate)

		annotations_tree_view = create_annotations_tree_view(self, annotations_tree_model, self.filter_data_service)
		annotations_tree_view_delegate = QStyledItemViewDelegate(
			FilterAnnotationViewDelegate(AbstractItemViewDelegate(), self.filter_data_service))
		annotations_tree_view.setItemDelegate(annotations_tree_view_delegate)
		annotation_tree_view_sub_window = MdiSubWindow(self)
		annotation_tree_view_sub_window.setWidget(annotations_tree_view)
		annotations_tree_sub_window = self.annotations_tree_mdi.addSubWindow(annotation_tree_view_sub_window)
		annotation_service = DeepableAnnotationService(root=annotations_tree_model)
		annotations_tree_sub_window.annotation_service = annotation_service
		# Be careful. Show will call activated signal => synchronization logic will be performed which requires "active annotation_service",
		# so need to set service(anything required for sync method) before showing.
		annotations_tree_sub_window.show()

		slide_path_provider = lambda: view.slide_helper.slide_path
		scene_provider = lambda: view.scene()

		filter_processor = create_filter_processor(self.filter_plugins)
		annotation_filter_processor = AnnotationFilterProcessor(pool=self.pool,
																slide_path_provider=slide_path_provider,
																annotation_service=annotation_service,
																filter_data_service=self.filter_data_service,
																filter_processor=filter_processor)
		# annotations_tree_model_delegate.annotation_item_pixmap_provider = annotation_filter_processor

		graphics_view_annotation_service = GraphicsViewAnnotationService3(scene_provider=scene_provider,
																		  scale_provider=None)
		view = GraphicsView(parent_=self,
							annotation_service=annotation_service,
							graphics_view_annotation_service=graphics_view_annotation_service,
							annotation_pixmap_provider=annotation_filter_processor, thread_pool=self.pool)
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
			self.view_mdi.activateWindow()

		def on_about_to_close():
			print("on_about_to_close", view_sub_window)
			self.sync_graphics_views(view)

		sync_about_to_activate(view_sub_window, annotation_tree_view_sub_window)
		sync_close(view_sub_window, annotation_tree_view_sub_window)
		view_sub_window.aboutToClose.connect(on_about_to_close)
		view.filePathChanged.connect(on_file_path_changed)
		view.filePathDropped.connect(on_file_path_dropped)

		sync_graphics_and_model_filters(self.filters_tree_view, view)
		sync_filtered_annotation_graphics_item_and_model_annotations(view, annotation_service)
		sync_annotations_stats(annotation_service, lambda: view.get_microns_per_pixel())
		sync_graphics_and_model_annotations(graphics_view_annotation_service, annotation_service)
		sync_graphics_and_model_selection(annotations_tree_view, view)

		return view_sub_window

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
