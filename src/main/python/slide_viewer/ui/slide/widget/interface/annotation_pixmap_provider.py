from abc import ABC, abstractmethod
from typing import Optional, Tuple

from PyQt5.QtGui import QPixmap


class AnnotationItemPixmapProvider(ABC):
    @abstractmethod
    def get_pixmap(self, annotation_id: str, ready_callback) -> Optional[Tuple[int, QPixmap]]:
        pass
