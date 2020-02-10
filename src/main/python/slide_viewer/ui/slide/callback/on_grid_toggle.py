from slide_viewer.ui.slide.graphics.view.graphics_view import GraphicsView


def on_grid_toggle(view: GraphicsView, visible: bool) -> None:
    view.set_grid_visible(visible)
