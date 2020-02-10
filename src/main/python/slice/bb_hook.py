from abc import ABC, abstractmethod
from typing import Tuple

from dataclasses import dataclass

from shapely_utils import ProbablyContainsChecker


class BBGeometryHook(ABC):
    @abstractmethod
    def filter(self, p1: Tuple[int, int], p2: Tuple[int, int]) -> bool:
        pass


@dataclass
class BBGeometryProbablyContainsHook(BBGeometryHook):
    probably_contains_checker: ProbablyContainsChecker

    def filter(self, p1: Tuple[int, int], p2: Tuple[int, int]) -> bool:
        return self.probably_contains_checker.probably_contains(p1[0], p1[1], p2[0], p2[1])