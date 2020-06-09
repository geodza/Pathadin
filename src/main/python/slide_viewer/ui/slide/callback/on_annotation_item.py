from annotation.annotation_type import AnnotationType
from slide_viewer.ui.slide.graphics.view.graphics_view import GraphicsView


def on_selection_tool(view: GraphicsView) -> None:
    view.graphics_view_annotation_service.cancel_annotation_if_any()
    view.graphics_view_annotation_service.annotation_type = None


def on_annotation_item(view: GraphicsView, annotation_type: AnnotationType) -> None:
    view.graphics_view_annotation_service.cancel_annotation_if_any()
    view.graphics_view_annotation_service.annotation_type = annotation_type
