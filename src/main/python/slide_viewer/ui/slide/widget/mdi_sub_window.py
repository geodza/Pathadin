import typing

from PyQt5 import QtCore, QtGui
from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtGui import QMouseEvent, QWheelEvent
from PyQt5.QtWidgets import QWidget, QMdiSubWindow


class MdiSubWindow(QMdiSubWindow):
    aboutToClose = pyqtSignal()

    def __init__(self, parent: typing.Optional[QWidget] = None,
                 flags: typing.Union[QtCore.Qt.WindowFlags, QtCore.Qt.WindowType] = Qt.WindowFlags()) -> None:
        QMdiSubWindow.__init__(self, parent, flags)
        self.setAttribute(Qt.WA_DeleteOnClose, True)

    def setWidget(self, widget: QWidget) -> None:
        super().setWidget(widget)
        widget.installEventFilter(self)

    def eventFilter(self, object: QtCore.QObject, event: QtCore.QEvent) -> bool:
        if isinstance(event, (QMouseEvent, QWheelEvent)):
            # print(event)
            self.setFocus()
            self.widget().setFocus()
            # return True
        return super().eventFilter(object, event)

    def closeEvent(self, closeEvent: QtGui.QCloseEvent) -> None:
        self.aboutToClose.emit()
        super().closeEvent(closeEvent)
