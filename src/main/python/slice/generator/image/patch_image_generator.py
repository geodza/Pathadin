from abc import ABC, abstractmethod

from slice.model.patch_geometry import PatchGeometryIterable
from slice.model.patch_image import PatchImageIterable


class PatchImageGenerator(ABC):
    @abstractmethod
    def create(self, patch_geometries: PatchGeometryIterable) -> PatchImageIterable:
        pass
