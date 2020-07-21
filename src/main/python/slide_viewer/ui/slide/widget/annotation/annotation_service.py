from abc import ABC, abstractmethod
from typing import List, Dict, Tuple

from PyQt5.QtCore import pyqtBoundSignal

from filter.common.filter_results import FilterResults
from annotation.model import AnnotationModel, AnnotationStats

ituple = Tuple[int, int]

class AnnotationService(ABC):

    @abstractmethod
    def get(self, id_: str) -> AnnotationModel:
        pass

    @abstractmethod
    def has(self, id_: str) -> bool:
        pass

    @abstractmethod
    def get_dict(self) -> Dict[str, AnnotationModel]:
        pass

    @abstractmethod
    def get_first_point(self, id_: str) -> ituple:
        pass

    @abstractmethod
    def add(self, model: AnnotationModel) -> AnnotationModel:
        pass

    @abstractmethod
    def add_copy_or_edit_with_copy(self, model: AnnotationModel) -> AnnotationModel:
        pass

    @abstractmethod
    def add_or_edit(self, id_: str, model: AnnotationModel) -> AnnotationModel:
        pass

    @abstractmethod
    def add_or_edit_with_copy(self, id_: str, model: AnnotationModel) -> AnnotationModel:
        pass

    @abstractmethod
    def add_or_edit_with_copy_without_filter(self, id_: str, model: AnnotationModel) -> AnnotationModel:
        pass

    @abstractmethod
    def edit_origin_point(self, id_: str, p: ituple) -> None:
        pass

    @abstractmethod
    def edit_last_point(self, id_: str, p: ituple) -> None:
        pass

    @abstractmethod
    def edit_filter_results(self, id_: str, filter_results: FilterResults) -> None:
        pass

    @abstractmethod
    def edit_stats(self, id_: str, stats: AnnotationStats) -> None:
        pass

    @abstractmethod
    def add_point(self, id_: str, p: ituple) -> None:
        pass

    @abstractmethod
    def delete(self, ids: List[str]) -> None:
        pass

    @abstractmethod
    def delete_if_exist(self, ids: List[str]) -> None:
        pass

    @abstractmethod
    def delete_all(self) -> None:
        pass

    @abstractmethod
    def get_next_id(self) -> str:
        pass

    @abstractmethod
    def added_signal(self) -> pyqtBoundSignal(AnnotationModel):
        pass

    @abstractmethod
    def edited_signal(self) -> pyqtBoundSignal(str, AnnotationModel):
        pass

    @abstractmethod
    def deleted_signal(self) -> pyqtBoundSignal(list):
        pass
