from abc import ABC, abstractmethod

from slide_viewer.ui.odict.deep.model import AnnotationModel


class AnnotationModelProvider(ABC):

    @abstractmethod
    def get_annotation_model(self, annotation_id: str) -> AnnotationModel:
        pass
