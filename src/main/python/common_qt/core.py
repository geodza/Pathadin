import typing

from PyQt5 import QtCore
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QMdiArea, QWidget, QDockWidget, QMenu, QAction


class QMdiAreaP(QMdiArea):

	def __init__(self, parent: typing.Optional[QWidget] = None,
				 view_mode: QMdiArea.ViewMode = QMdiArea.SubWindowView) -> None:
		super().__init__(parent)
		self.setViewMode(view_mode)


class QDockWidgetP(QDockWidget):

	def __init__(self, title: str, parent: typing.Optional[QWidget] = None,
				 flags: typing.Union[QtCore.Qt.WindowFlags, QtCore.Qt.WindowType] = Qt.WindowFlags(),
				 widget: QWidget = None,
				 features: QDockWidget.DockWidgetFeatures = QDockWidget.DockWidgetClosable | QDockWidget.DockWidgetMovable | QDockWidget.DockWidgetFloatable) -> None:
		super().__init__(title, parent, flags)
		self.setWidget(widget)
		self.setFeatures(features)


class QMenuP(QMenu):

	def __init__(self, title: str, parent: typing.Optional[QWidget] = None, actions: typing.List[QAction] = []):
		super().__init__(title, parent)
		self.addActions(actions)
