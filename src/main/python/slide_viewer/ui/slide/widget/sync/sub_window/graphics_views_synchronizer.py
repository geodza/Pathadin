from typing import List, Callable, Optional

from dataclasses import dataclass, field

from slide_viewer.ui.slide.graphics.view.graphics_view import GraphicsView


@dataclass(frozen=True)
class GraphicsViewSyncOptions:
	view_transform: bool = False
	grid_visible: bool = False
	grid_size: bool = False
	file_path: bool = False
	background_brush: bool = False
	annotation_selection: bool = False


def sync_graphics_sub_views(view: GraphicsView, sub_views_except_active: List[GraphicsView],
							options: GraphicsViewSyncOptions) \
		-> Callable[[], None]:
	def cleanup():
		view.setDisabled(True)
		# print(f'cleanup --------------')
		# print(f'cleanup {id(view)}')
		for sub_view in sub_views_except_active:
			if options.view_transform:
				view.transformChanged.disconnect(sub_view.setTransform)
				view.viewUpdated.disconnect(sub_view.update)
				view.viewSceneRectUpdated.disconnect(sub_view.updateSceneRect)
				view.viewSceneRectsUpdated.disconnect(sub_view.updateScene)
			if options.grid_visible:
				view.gridVisibleChanged.disconnect(sub_view.set_grid_visible)
			if options.grid_size:
				view.gridSizeChanged.disconnect(sub_view.set_grid_size)
				view.gridSizeIsInPixelsChanged.disconnect(sub_view.set_grid_size_is_in_pixels)
			if options.file_path:
				view.filePathChanged.disconnect(sub_view.set_file_path)
			if options.background_brush:
				view.backgroundBrushChanged.disconnect(sub_view.set_background_brush)
			if options.annotation_selection:
				view.scene().annotationModelsSelected.disconnect(sub_view.scene().select_annotations)

	for sub_view in sub_views_except_active:
		if options.view_transform:
			view.transformChanged.connect(sub_view.setTransform)
			view.viewUpdated.connect(sub_view.update)
			view.viewSceneRectUpdated.connect(sub_view.updateSceneRect)
			view.viewSceneRectsUpdated.connect(sub_view.updateScene)
		if options.grid_visible:
			view.gridVisibleChanged.connect(sub_view.set_grid_visible)
		if options.grid_size:
			view.gridSizeChanged.connect(sub_view.set_grid_size)
			view.gridSizeIsInPixelsChanged.connect(sub_view.set_grid_size_is_in_pixels)
		if options.file_path:
			view.filePathChanged.connect(sub_view.set_file_path)
		if options.background_brush:
			view.backgroundBrushChanged.connect(sub_view.set_background_brush)
		if options.annotation_selection:
			view.scene().annotationModelsSelected.connect(sub_view.scene().select_annotations)
	view.setDisabled(False)
	return cleanup


class GraphicsViewsSynchronizer:
	def __init__(self):
		self._cleanup = None

	def sync(self, _source: GraphicsView,
			 _targets: List[GraphicsView],
			 _options: GraphicsViewSyncOptions,
			 ):
		if self._cleanup:
			self._cleanup()
			self._cleanup = None
		if _source:
			view = _source
			sub_views_except_active = [sw for sw in _targets if sw is not view]
			# print(f"active view: {view}")
			cleanup = sync_graphics_sub_views(view, sub_views_except_active, _options)
			self._cleanup = cleanup
