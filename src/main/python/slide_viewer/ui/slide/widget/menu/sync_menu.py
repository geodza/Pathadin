from typing import Optional

from PyQt5.QtWidgets import QMenu, QWidget
from dataclasses import dataclass, InitVar

from slide_viewer.ui.slide.action.sync_action_group import SyncActionGroup


@dataclass
class SyncMenu(QMenu):
    parent_: InitVar[Optional[QWidget]]
    sync_action_group: InitVar[SyncActionGroup]
    title_: InitVar[str] = "Sync"

    def __post_init__(self, parent_: Optional[QWidget], sync_action_group: SyncActionGroup, title_: str):
        super().__init__(parent_)
        self.setTitle(title_)
        self.addActions([
            *sync_action_group.actions()
        ])
        self.setIcon(sync_action_group.sync_all_action.icon())
        self.sync_all_action = sync_action_group.sync_all_action
