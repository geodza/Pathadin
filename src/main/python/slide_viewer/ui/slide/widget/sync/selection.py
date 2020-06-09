import typing

from PyQt5.QtCore import QRectF

from common_qt.util.slot_disconnected_utils import slot_disconnected
from deepable.core import toplevel_keys
from deepable_qt.view.deepable_tree_view import DeepableTreeView
from slide_viewer.ui.slide.graphics.view.graphics_view import GraphicsView


def sync_graphics_and_model_selection(tree_view: DeepableTreeView, graphics_view: GraphicsView) -> None:
	def on_items_selected(ids: typing.List[str]):
		with slot_disconnected(tree_view.objectsSelected, on_models_selected):
			tree_view.select_keys(ids)

	def on_models_selected(keys: typing.List[str]):
		with slot_disconnected(graphics_view.scene().annotationModelsSelected, on_items_selected):
			ids = toplevel_keys(keys) & set(keys)
			annotations_bounding_rect = QRectF()
			for id_, annotation in graphics_view.scene().annotations.items():
				if id_ in ids:
					annotation.setSelected(True)
					annotation_bounding_rect = annotation.boundingRect().translated(annotation.pos())
					annotations_bounding_rect = annotations_bounding_rect.united(annotation_bounding_rect)
				else:
					annotation.setSelected(False)
			if annotations_bounding_rect:
				graphics_view.fit_rect(annotations_bounding_rect)

	graphics_view.scene().annotationModelsSelected.connect(on_items_selected)
	tree_view.objectsSelected.connect(on_models_selected)