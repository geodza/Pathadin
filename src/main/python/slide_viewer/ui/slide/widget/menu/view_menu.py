from typing import Optional

from PyQt5.QtWidgets import QMenu, QWidget
from dataclasses import dataclass, InitVar

from slide_viewer.ui.slide.action.simple_actions import SimpleActions, ActionType


@dataclass
class ViewMenu(QMenu):
    parent_: InitVar[Optional[QWidget]]
    simple_actions: InitVar[SimpleActions]
    title_: InitVar[str] = "View"

    def __post_init__(self, parent_: Optional[QWidget], simple_actions: SimpleActions, title_: str):
        super().__init__(parent_)
        self.setTitle(title_)
        d = simple_actions.actions
        self.addActions([
            d[ActionType.open],
            d[ActionType.slide_properties],
            d[ActionType.take_screenshot],
            d[ActionType.take_screenshot_to_clipboard],
            d[ActionType.view_background_color],
            d[ActionType.export_annotations],
            d[ActionType.import_annotations]
        ])
