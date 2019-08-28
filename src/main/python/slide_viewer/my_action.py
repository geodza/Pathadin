from typing import Union, List

from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import QAction, QMenu, QToolBar


class MyAction(QAction):
    def __init__(self, title, parent: Union[QMenu, QToolBar], action_func=None, icon: QIcon = None,
                 data=None):
        super().__init__(title, parent)
        self.window = None
        if isinstance(parent, QMenu) or isinstance(parent, QToolBar):
            self.window = parent.parent()
            parent.addAction(self)
        if action_func:
            self.triggered.connect(action_func)
        if icon:
            self.setIcon(icon)
        if data:
            self.setData(data)
