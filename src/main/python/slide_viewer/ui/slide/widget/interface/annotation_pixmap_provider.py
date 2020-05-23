from abc import ABC, abstractmethod
from typing import Optional, Tuple, Callable

from PyQt5.QtGui import QPixmap


class AnnotationItemPixmapProvider(ABC):
	@abstractmethod
	def get_pixmap(self, annotation_id: str, ready_callback: Callable[[], None]) -> Optional[Tuple[int, QPixmap]]:
		pass
