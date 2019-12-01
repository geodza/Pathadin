from slide_viewer.ui.slide.graphics.graphics_view import GraphicsView


def on_zoom(view: GraphicsView, scale: float) -> None:
    view.set_scale_in_view_center(scale)
