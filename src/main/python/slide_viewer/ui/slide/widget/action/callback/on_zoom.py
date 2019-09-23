from slide_viewer.ui.slide.graphics.slide_viewer_graphics_view import SlideViewerGraphicsView


def on_zoom(view: SlideViewerGraphicsView, scale):
    view.set_scale_in_view_center(scale)
