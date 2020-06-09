from abc import ABC, abstractmethod
from PyQt5.QtCore import QPoint


class ContextMenuDelegate(ABC):

	@abstractmethod
	def on_context_menu(self, position: QPoint) -> None:
		pass
