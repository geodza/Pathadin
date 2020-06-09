from typing import Optional, Iterable

from PyQt5.QtWidgets import QMenu, QMenuBar, QAction, QWidget


class MyMenu(QMenu):
	def __init__(self, title, parent):
		super().__init__(title, parent)
		self.window = None
		if isinstance(parent, QMenu) or isinstance(parent, QMenuBar):
			self.window = parent.parent()
			parent.addMenu(self)


def create_menu(title: str, actions: Iterable[QAction], parent: Optional[QWidget] = None) -> QMenu:
	menu = QMenu(title, parent)
	for a in actions:
		a.setParent(menu)
		menu.addAction(a)
	return menu
