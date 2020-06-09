from typing import Optional, Tuple, Callable

from PyQt5.QtCore import QSize
from PyQt5.QtWidgets import QToolBar, QWidget
from dataclasses import dataclass, InitVar

from common_qt.action.separator_action import SeparatorAction
from slide_viewer.ui.slide.action.annotation_action_group import AnnotationActionGroup
from slide_viewer.ui.slide.action.simple_actions import SimpleActions, ActionType
from slide_viewer.ui.slide.action.zoom_action_group import ZoomActionGroup
from slide_viewer.ui.slide.action.zoom_editor import ZoomEditor
from slide_viewer.ui.slide.widget.menu.sync_menu import SyncMenu
from slide_viewer.ui.slide.widget.menu.sync_tool_button import SyncToolButton


@dataclass
class Toolbar(QToolBar):
    parent_: InitVar[Optional[QWidget]]
    simple_actions: InitVar[SimpleActions]
    zoom_action_group: InitVar[ZoomActionGroup]
    annotation_action_group: InitVar[AnnotationActionGroup]
    sync_menu: InitVar[SyncMenu]
    zoom_editor: InitVar[ZoomEditor]
    spacing: InitVar[int] = 5
    icon_size: InitVar[Tuple[int, int]] = (24, 24)

    def __post_init__(self, parent_: Optional[QWidget], simple_actions: SimpleActions,
                      zoom_action_group: ZoomActionGroup, annotation_action_group: AnnotationActionGroup,
                      sync_menu: SyncMenu, zoom_editor: ZoomEditor, spacing: int,
                      icon_size: Tuple[int, int]):
        super().__init__('Main toolbar', parent_)
        self.layout().setSpacing(spacing)
        self.setIconSize(QSize(*icon_size))
        self.cleanup: Optional[Callable[[], None]] = None
        d = simple_actions.actions
        self.addActions([
            d[ActionType.add_sub_window],
            d[ActionType.tile_sub_windows],
        ])
        self.addWidget(SyncToolButton(parent_=parent_, sync_menu=sync_menu))
        self.addActions([
            SeparatorAction(self),
            d[ActionType.open],
            d[ActionType.slide_properties],
            d[ActionType.toggle_grid],
            d[ActionType.take_screenshot],
            d[ActionType.take_screenshot_to_clipboard],
            SeparatorAction(self),
            *annotation_action_group.actions(),
            SeparatorAction(self),
            d[ActionType.fit],
        ])
        self.addWidget(zoom_editor)

        def zoom_actions_changed():
            if self.cleanup:
                self.cleanup()
                self.cleanup = None

            actions = zoom_action_group.actions()

            def cleanup():
                for action in actions:
                    self.removeAction(action)

            for action in actions:
                self.addAction(action)
            self.cleanup = cleanup

        zoom_action_group.zoomActionsChanged.connect(zoom_actions_changed)
