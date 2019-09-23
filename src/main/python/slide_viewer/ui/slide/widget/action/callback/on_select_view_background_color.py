from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QColorDialog

from slide_viewer.ui.slide.graphics.slide_viewer_graphics_view import SlideViewerGraphicsView


def on_select_view_background_color(view: SlideViewerGraphicsView):
    def on_background_color_change(color):
        view.setBackgroundBrush(color)

    color_dialog = QColorDialog(Qt.white, view)
    color_dialog.setOptions(QColorDialog.ShowAlphaChannel)
    last_color = view.backgroundBrush().color()
    color_dialog.currentColorChanged.connect(on_background_color_change)
    color_dialog.colorSelected.connect(on_background_color_change)
    res = color_dialog.exec()
    if not res:
        view.setBackgroundBrush(last_color)
