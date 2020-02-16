from abc import ABC
from typing import Tuple

from dataclasses import dataclass

from common.grid_utils import pos_range
from slice.model.patch_pos import PatchPosIterable

@dataclass
class PatchPosGenerator(ABC):
    source_size: Tuple[int, int]
    stride: int
    x_offset: int = 0
    y_offset: int = 0

    # @abstractmethod
    def create(self) -> PatchPosIterable:
        return pos_range(self.source_size, self.stride, self.x_offset, self.y_offset)
