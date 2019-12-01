from slide_viewer.ui.model.annotation_type import AnnotationType
from slide_viewer.ui.slide.graphics.graphics_view import GraphicsView


def on_selection_tool(view: GraphicsView) -> None:
    view.on_off_annotation()
    view.annotation_type = None


def on_annotation_item(view: GraphicsView, annotation_type: AnnotationType) -> None:
    view.on_off_annotation()
    view.annotation_type = annotation_type
