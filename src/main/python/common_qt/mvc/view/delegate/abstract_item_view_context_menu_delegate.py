from abc import ABC, abstractmethod
from typing import TypeVar, Generic, Optional

from PyQt5.QtCore import QModelIndex, QPoint
from PyQt5.QtWidgets import QAbstractItemView, QMenu

from common_qt.action.context_menu_delegate import ContextMenuDelegate

I = TypeVar('I', bound=QModelIndex)
V = TypeVar('V', bound=QAbstractItemView)


class AbstractItemViewContextMenuDelegate(ContextMenuDelegate, ABC, Generic[I, V]):

	def __init__(self, view: V):
		self.view = view

	def on_context_menu(self, position: QPoint) -> None:
		# print("on_context_menu")
		index = self.view.indexAt(position)
		menu = self.create_menu(index)
		if menu:
			# menu.setParent(self.view)
			# menu.exec_(self.view.viewport().mapToGlobal(position))
			menu.exec(self.view.viewport().mapToGlobal(position))

	@abstractmethod
	def create_menu(self, index: I) -> Optional[QMenu]:
		pass
