from typing import Optional, Callable

from PyQt5.QtWidgets import QMenu, QWidget
from dataclasses import dataclass, InitVar

from common_qt.action.separator_action import SeparatorAction
from slide_viewer.ui.slide.action.simple_actions import SimpleActions, ActionType
from slide_viewer.ui.slide.action.zoom_action_group import ZoomActionGroup


@dataclass
class ZoomMenu(QMenu):
    parent_: InitVar[Optional[QWidget]]
    simple_actions: InitVar[SimpleActions]
    zoom_action_group: InitVar[ZoomActionGroup]
    title_: InitVar[str] = "Zoom"

    def __post_init__(self, parent_: Optional[QWidget], simple_actions: SimpleActions,
                      zoom_action_group: ZoomActionGroup, title_: str):
        super().__init__(parent_)
        self.setTitle(title_)
        self.cleanup: Optional[Callable[[], None]] = None
        d = simple_actions.actions
        self.addActions([
            d[ActionType.fit],
            SeparatorAction(self)
        ])

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
