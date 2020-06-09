from abc import ABC, abstractmethod
from typing import Optional

from deepable_qt.view.deepable_tree_view import DeepableTreeView
from slide_viewer.ui.slide.widget.annotation.annotation_service import AnnotationService


class ActiveAnnotationServiceProvider(ABC):
    @property
    @abstractmethod
    def active_annotation_service(self) -> Optional[AnnotationService]:
        pass
