import typing

from PyQt5.QtWidgets import QToolButton, QWidget
from dataclasses import dataclass, InitVar

from slide_viewer.ui.slide.widget.menu.sync_menu import SyncMenu


@dataclass
class SyncToolButton(QToolButton):
    parent_: InitVar[typing.Optional[QWidget]]
    sync_menu: InitVar[SyncMenu]

    def __post_init__(self, parent_: typing.Optional[QWidget], sync_menu: SyncMenu):
        super().__init__(parent_)
        sync_tool_button = self
        sync_tool_button.setMenu(sync_menu)
        sync_tool_button.setPopupMode(QToolButton.InstantPopup)
        sync_all_action = sync_menu.sync_all_action
        sync_tool_button.setCheckable(True)
        sync_all_action.changed.connect(lambda: sync_tool_button.setChecked(sync_all_action.isChecked()))
        sync_tool_button.setIcon(sync_all_action.icon())
