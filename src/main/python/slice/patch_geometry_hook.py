from abc import ABC, abstractmethod

from slice.patch_geometry import PatchGeometry


class PatchGeometryHook(ABC):
    @abstractmethod
    def filter(self, patch_geometry: PatchGeometry) -> bool:
        pass


