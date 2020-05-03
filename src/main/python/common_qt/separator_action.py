from typing import Optional

from PyQt5.QtCore import QObject
from PyQt5.QtWidgets import QAction


class SeparatorAction(QAction):
	def __init__(self, parent: Optional[QObject] = None) -> None:
		super().__init__(parent)
		self.setSeparator(True)
