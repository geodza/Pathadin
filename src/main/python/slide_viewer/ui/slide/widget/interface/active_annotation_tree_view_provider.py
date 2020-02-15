from abc import ABC, abstractmethod
from typing import Optional

from deepable_qt.deepable_tree_view import DeepableTreeView


class ActiveAnnotationTreeViewProvider(ABC):
    @property
    @abstractmethod
    def active_annotation_tree_view(self) -> Optional[DeepableTreeView]:
        pass
