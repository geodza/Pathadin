from abc import abstractmethod, ABC
from typing import Iterable, Callable

import numpy as np

from ndarray_persist.common import stack_ndarrays, NamedNdarray


class NdarrayLoader(ABC):
    def __init__(self, ndarray_converter: Callable[[np.ndarray], np.ndarray] = None):
        self.ndarray_converter = ndarray_converter

    @abstractmethod
    def load_names(self) -> Iterable[str]:
        pass

    @abstractmethod
    def load_ndarrays(self) -> Iterable[np.ndarray]:
        pass

    def load_named_ndarrays(self) -> Iterable[NamedNdarray]:
        return zip(self.load_names(), self.load_ndarrays())

    def stack_ndarrays(self):
        names = list(self.load_names())
        ndarrays = self.load_ndarrays()
        return stack_ndarrays(ndarrays, len(names))
