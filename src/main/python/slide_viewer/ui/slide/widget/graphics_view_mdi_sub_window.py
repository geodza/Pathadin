import typing

from PyQt5 import QtCore
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QWidget, QMdiSubWindow

from slide_viewer.ui.slide.graphics.graphics_view import GraphicsView
from slide_viewer.ui.slide.widget.mdi_sub_window import MdiSubWindow


class GraphicsViewMdiSubWindow(MdiSubWindow):

    def __init__(self, parent: typing.Optional[QWidget] = None,
                 flags: typing.Union[QtCore.Qt.WindowFlags, QtCore.Qt.WindowType] = Qt.WindowFlags()) -> None:
        MdiSubWindow.__init__(self, parent, flags)

    def widget(self) -> GraphicsView:
        return typing.cast(GraphicsView, QMdiSubWindow.widget(self))

    def setWidget(self, widget: GraphicsView) -> None:
        super().setWidget(widget)
        widget.installEventFilter(self)
