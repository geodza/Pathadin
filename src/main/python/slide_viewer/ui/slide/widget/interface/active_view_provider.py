from abc import ABC, abstractmethod
from typing import Optional

from slide_viewer.ui.slide.graphics.graphics_view import GraphicsView


class ActiveViewProvider(ABC):
    @property
    @abstractmethod
    def active_view(self) -> Optional[GraphicsView]:
        pass
