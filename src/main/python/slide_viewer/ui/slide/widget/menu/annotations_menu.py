from typing import Optional

from PyQt5.QtWidgets import QMenu, QWidget
from dataclasses import dataclass, InitVar

from slide_viewer.ui.slide.action.annotation_action_group import AnnotationActionGroup


@dataclass
class AnnotationsMenu(QMenu):
    parent_: InitVar[Optional[QWidget]]
    annotation_action_group: InitVar[AnnotationActionGroup]
    title_: InitVar[str] = "Annotations"

    def __post_init__(self, parent_: Optional[QWidget], annotation_action_group: AnnotationActionGroup, title_: str):
        super().__init__(parent_)
        self.setTitle(title_)
        self.addActions([
            *annotation_action_group.actions()
        ])
