from abc import ABC, abstractmethod

from slice.model.patch_geometry import PatchGeometry


class PatchGeometryHook(ABC):
    @abstractmethod
    def filter(self, patch_geometry: PatchGeometry) -> bool:
        pass


