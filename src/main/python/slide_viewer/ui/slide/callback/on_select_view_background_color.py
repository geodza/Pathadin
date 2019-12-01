from PyQt5.QtCore import Qt
from PyQt5.QtGui import QBrush, QColor
from PyQt5.QtWidgets import QColorDialog

from slide_viewer.ui.slide.graphics.graphics_view import GraphicsView


def on_select_view_background_color(view: GraphicsView) -> None:
    def on_background_color_change(color: QColor):
        view.set_background_brush(QBrush(color))

    color_dialog = QColorDialog(Qt.white, view)
    color_dialog.setOptions(QColorDialog.ShowAlphaChannel)
    last_color = view.get_background_brush().color()
    color_dialog.currentColorChanged.connect(on_background_color_change)
    color_dialog.colorSelected.connect(on_background_color_change)
    res = color_dialog.exec()
    if not res:
        view.set_background_brush(last_color)
