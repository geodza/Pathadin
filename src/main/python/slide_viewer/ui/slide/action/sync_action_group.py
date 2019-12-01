from typing import Optional, Callable

from PyQt5.QtCore import QObject
from PyQt5.QtWidgets import QActionGroup
from dataclasses import InitVar, dataclass

from slide_viewer.ui.common.action.my_action import MyAction
from slide_viewer.ui.common.disability.decorator import subscribe_disableable
from slide_viewer.ui.slide.callback.sub_window.on_sync_sub_windows import on_sync_option
from slide_viewer.ui.slide.widget.icons import IconName
from slide_viewer.ui.slide.widget.interface.active_view_provider import ActiveViewProvider
from slide_viewer.ui.slide.widget.interface.icon_provider import IconProvider
from slide_viewer.ui.slide.widget.interface.mdi_sub_window_service import SubWindowService, SyncOption


@dataclass
class SyncActionGroup(QActionGroup):
    parent_: InitVar[Optional[QObject]]
    active_view_provider: InitVar[ActiveViewProvider]
    sub_window_service: InitVar[SubWindowService]
    icon_provider: InitVar[IconProvider]

    def __post_init__(self, parent_: Optional[QObject], active_view_provider: ActiveViewProvider,
                      sub_window_service: SubWindowService, icon_provider: IconProvider):
        super().__init__(parent_)
        self.cleanup: Optional[Callable[[], None]] = None

        def sync_closure(sync_option: SyncOption):
            def f(checked: bool):
                on_sync_option(sub_window_service, sync_option, checked)

            return f

        def is_active_view_present() -> bool:
            view = active_view_provider.active_view
            return view is not None

        sync_all_action = MyAction("Sync all", self, sync_closure(SyncOption.all),
                                   icon_provider.get_icon(IconName.sync))
        single_actions = [
            MyAction("Sync view transform", self, sync_closure(SyncOption.view_transform)),
            MyAction("Sync file path", self, sync_closure(SyncOption.file_path)),
            MyAction("Sync grid visible", self, sync_closure(SyncOption.grid_visible)),
            MyAction("Sync grid size", self, sync_closure(SyncOption.grid_size)),
            MyAction("Sync background brush", self, sync_closure(SyncOption.background_brush)),
            MyAction("Sync annotations", self, sync_closure(SyncOption.annotations)),
        ]

        def on_sync_all(checked: bool):
            for action in self.actions():
                action.setChecked(checked)

        def on_sync_one(checked: bool):
            all_checked = all([action.isChecked() for action in single_actions])
            sync_all_action.setChecked(all_checked)

        self.setExclusive(False)
        for action in single_actions:
            action.setCheckable(True)
            subscribe_disableable([sub_window_service.sub_window_activated], is_active_view_present, action)
            action.triggered.connect(on_sync_one)
        sync_all_action.setCheckable(True)
        subscribe_disableable([sub_window_service.sub_window_activated], is_active_view_present, sync_all_action)
        sync_all_action.triggered.connect(on_sync_all)

        self.sync_all_action = sync_all_action
