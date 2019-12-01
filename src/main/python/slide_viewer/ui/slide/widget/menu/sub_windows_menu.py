from typing import Optional

from PyQt5.QtWidgets import QMenu, QWidget
from dataclasses import dataclass, InitVar

from slide_viewer.ui.slide.action.simple_actions import SimpleActions, ActionType
from slide_viewer.ui.slide.widget.menu.sync_menu import SyncMenu


@dataclass
class SubWindowsMenu(QMenu):
    parent_: InitVar[Optional[QWidget]]
    simple_actions: InitVar[SimpleActions]
    sync_menu: InitVar[SyncMenu]
    title_: InitVar[str] = "Subwindows"

    def __post_init__(self, parent_: Optional[QWidget], simple_actions: SimpleActions, sync_menu: SyncMenu,
                      title_: str):
        super().__init__(parent_)
        self.setTitle(title_)
        d = simple_actions.actions
        self.addActions([
            d[ActionType.add_sub_window],
            d[ActionType.tile_sub_windows],
            # d[ActionType.sync_all]
        ])
        self.addMenu(sync_menu)
