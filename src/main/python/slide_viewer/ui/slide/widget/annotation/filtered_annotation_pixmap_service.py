from typing import Callable, Optional, Tuple

from PyQt5.QtGui import QPixmap, QPixmapCache
from dataclasses import dataclass

from slide_viewer.ui.slide.widget.interface.annotation_pixmap_provider import AnnotationItemPixmapProvider

@dataclass
class FilteredAnnotationPixmapService(AnnotationItemPixmapProvider):

	def get_pixmap(self, annotation_id: str, ready_callback: Callable[[], None]) -> Optional[Tuple[int, QPixmap]]:


		pixmap_cache_key = f'filtered_annotation_pixmap_{annotation_id}'
		pixmap = QPixmapCache.find(pixmap_cache_key)
		pass