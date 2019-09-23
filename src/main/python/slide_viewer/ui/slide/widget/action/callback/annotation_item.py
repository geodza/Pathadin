from slide_viewer.ui.slide.graphics.annotation.annotation_type import AnnotationType
from slide_viewer.ui.slide.widget.slide_viewer_widget import SlideViewerWidget


def on_selection_tool(w: SlideViewerWidget):
    w.view.annotation_type = None
    if w.view.annotation_item:
        w.scene.removeItem(w.view.annotation_item)
        w.view.annotation_item = None
        w.view.annotation_item_in_progress = False


def on_annotation_item(w: SlideViewerWidget, annotation_type: AnnotationType):
    w.view.annotation_type = annotation_type
    w.view.annotation_item_in_progress = False
