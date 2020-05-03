from typing import Union, List, Optional

from PyQt5 import QtCore
from PyQt5.QtCore import pyqtProperty
from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import QAction, QMenu, QToolBar, QActionGroup


class MyAction(QAction):

	def __init__(self, title: Optional[str] = None, parent: Optional[Union[QMenu, QToolBar, QActionGroup]] = None,
				 action_func=None,
				 icon: QIcon = None,
				 data=None):
		super().__init__(title, parent)
		self.window = None
		if isinstance(parent, QMenu) or isinstance(parent, QToolBar) or isinstance(parent, QActionGroup):
			self.window = parent.parent()
			parent.addAction(self)
		if action_func:
			self.triggered.connect(action_func)
		if icon:
			self.setIcon(icon)
		if data:
			self.setData(data)
