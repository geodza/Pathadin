from abc import ABC, abstractmethod


class ScaleProvider(ABC):
    @abstractmethod
    def get_scale(self) -> float:
        pass
