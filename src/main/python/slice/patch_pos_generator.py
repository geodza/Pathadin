from abc import ABC, abstractmethod
from typing import Tuple

from slice.patch_pos import PatchPosIterable


class PatchPosGenerator(ABC):
    @abstractmethod
    def create(self, source_size: Tuple[int, int], stride: int = None, x_offset: int = 0, y_offset: int = 0) \
            -> PatchPosIterable:
        pass
