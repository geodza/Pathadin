from abc import ABC
from typing import Tuple

from common.grid_utils import pos_range
from slice.model.patch_pos import PatchPosIterable


class PatchPosGenerator(ABC):
    # @abstractmethod
    def create(self, source_size: Tuple[int, int], stride: int, x_offset: int = 0, y_offset: int = 0) \
            -> PatchPosIterable:
        return pos_range(source_size, stride, x_offset, y_offset)
