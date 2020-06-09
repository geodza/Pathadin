from typing import List

from deepable_qt.view.deepable_tree_view import DeepableTreeView
from slide_viewer.ui.slide.graphics.view.graphics_view import GraphicsView


def sync_graphics_and_model_filters(tree_view: DeepableTreeView, graphics_view: GraphicsView):
	def tree_filter_models_changed(keys: List[str]):
		if graphics_view and graphics_view.filter_graphics_item:
			graphics_view.filter_graphics_item.update()

	tree_view.model().keysChanged.connect(tree_filter_models_changed)
