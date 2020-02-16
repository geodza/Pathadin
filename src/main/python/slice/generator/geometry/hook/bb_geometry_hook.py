from abc import ABC, abstractmethod
from typing import Tuple


class BBGeometryHook(ABC):
    @abstractmethod
    def filter(self, p1: Tuple[int, int], p2: Tuple[int, int]) -> bool:
        pass
