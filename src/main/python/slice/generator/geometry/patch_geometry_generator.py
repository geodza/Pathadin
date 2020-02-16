from abc import ABC, abstractmethod

from slice.model.patch_geometry import PatchGeometryIterable
from slice.model.patch_pos import PatchPosIterable


class PatchGeometryGenerator(ABC):
    @abstractmethod
    def create(self, patch_positions: PatchPosIterable) -> PatchGeometryIterable:
        pass
