from collections import OrderedDict
from typing import Dict

from PyQt5.QtCore import QObject, pyqtSignal
from PyQt5.QtWidgets import QGraphicsScene
from dataclasses import dataclass, field

from slide_viewer.common_qt.abcq_meta import ABCQMeta
from slide_viewer.ui.slide.graphics.item.annotation.annotation_graphics_item import AnnotationGraphicsItem
from slide_viewer.ui.slide.widget.interface.scale_view_provider import ScaleProvider


@dataclass
class GraphicsScene(QGraphicsScene, metaclass=ABCQMeta):
    scale_provider: ScaleProvider
    parent_: QObject = field(default=None)
    annotations: Dict[str, AnnotationGraphicsItem] = field(default_factory=OrderedDict)
    annotationModelsSelected = pyqtSignal(list)

    def __post_init__(self):
        super().__init__(self.parent_)
        self.selectionChanged.connect(self.__on_selection_changed)

    def __on_selection_changed(self) -> None:
        ids = [i.id for i in self.selectedItems() if isinstance(i, AnnotationGraphicsItem)]
        self.annotationModelsSelected.emit(ids)

    def __on_annotation_removed_from_scene(self, annotation_id: str):
        self.annotations.pop(annotation_id, None)

    def add_annotation(self, annotation: AnnotationGraphicsItem) -> None:
        self.annotations[annotation.id] = annotation
        annotation.signals.removedFromScene.connect(self.__on_annotation_removed_from_scene)
        self.addItem(annotation)

    def select_annotations(self, ids: list) -> None:
        for i, annotation in self.annotations.items():
            annotation.setSelected(i in ids)

    def remove_annotations(self, ids: list) -> None:
        for id in ids:
            if id not in self.annotations:
                # raise ValueError(f'Scene hasn\'t annotation with id: {id}')
                continue
            annotation = self.annotations[id]
            self.removeItem(annotation)

    def clear(self) -> None:
        # pure clear doesn't call ItemSceneHasChanged for items!!!
        self.clear_annotations()
        super().clear()

    def clear_annotations(self) -> None:
        for annotation in list(self.annotations.values()):
            self.removeItem(annotation)
