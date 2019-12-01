import typing

from PyQt5 import QtCore
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QMouseEvent, QWheelEvent
from PyQt5.QtWidgets import QWidget, QMdiSubWindow

from slide_viewer.ui.slide.graphics.graphics_view import GraphicsView


class MdiSubWindow(QMdiSubWindow):

    def __init__(self, parent: typing.Optional[QWidget] = None,
                 flags: typing.Union[QtCore.Qt.WindowFlags, QtCore.Qt.WindowType] = Qt.WindowFlags()) -> None:
        super().__init__(parent, flags)
        self.setAttribute(Qt.WA_DeleteOnClose, True)

    def widget(self) -> GraphicsView:
        return typing.cast(GraphicsView, QMdiSubWindow.widget(self))

    def setWidget(self, widget: GraphicsView) -> None:
        super().setWidget(widget)
        widget.installEventFilter(self)

    def eventFilter(self, object: QtCore.QObject, event: QtCore.QEvent) -> bool:
        if isinstance(event, (QMouseEvent, QWheelEvent)):
            # print(event)
            self.setFocus()
            self.widget().setFocus()
            # return True
        return super().eventFilter(object, event)
