from abc import ABC, abstractmethod


class SlideStatsProvider(ABC):
    @abstractmethod
    def get_microns_per_pixel(self) -> float:
        pass
