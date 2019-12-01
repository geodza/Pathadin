from abc import ABC, abstractmethod


class Disableable(ABC):
    @abstractmethod
    def setDisabled(self, disabled: bool) -> None:
        pass
