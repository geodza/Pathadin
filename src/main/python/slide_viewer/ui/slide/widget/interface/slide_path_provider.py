from abc import ABC, abstractmethod

class SlidePathProvider(ABC):

    @abstractmethod
    def get_slide_path(self) -> str:
        pass
