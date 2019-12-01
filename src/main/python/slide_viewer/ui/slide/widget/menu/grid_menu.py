from typing import Optional

from PyQt5.QtWidgets import QMenu, QWidget
from dataclasses import dataclass, InitVar

from slide_viewer.ui.slide.action.simple_actions import SimpleActions, ActionType


@dataclass
class GridMenu(QMenu):
    parent_: InitVar[Optional[QWidget]]
    simple_actions: InitVar[SimpleActions]
    title_: InitVar[str] = "Grid"

    def __post_init__(self, parent_: Optional[QWidget], simple_actions: SimpleActions, title_: str):
        super().__init__(parent_)
        self.setTitle(title_)
        d = simple_actions.actions
        self.addActions([
            d[ActionType.toggle_grid],
            d[ActionType.change_grid_size],
        ])
