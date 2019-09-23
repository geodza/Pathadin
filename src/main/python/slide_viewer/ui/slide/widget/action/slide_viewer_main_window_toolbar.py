from PyQt5.QtCore import QSize
from PyQt5.QtWidgets import QToolBar

from slide_viewer.ui.common.separator_action import SeparatorAction
from slide_viewer.ui.slide.widget.action.slide_viewer_main_window_simple_actions import MainWindowSimpleActions, ActionType
from slide_viewer.ui.slide.widget.action.slide_viewer_main_window_annotation_action_group import MainWindowAnnotationActionGroup
from slide_viewer.ui.slide.widget.action.slide_viewer_main_window_zoom_action_group import MainWindowZoomActionGroup
from slide_viewer.ui.slide.widget.action.slide_viewer_main_window_zoom_editor import SlideViewerMainWindowZoomEditor


class SlideViewerMainWindowToolbar(QToolBar):

    def __init__(self, mw, ctx, simple_actions: MainWindowSimpleActions,
                 zoom_action_group: MainWindowZoomActionGroup,
                 annotation_action_group: MainWindowAnnotationActionGroup,
                 zoom_editor: SlideViewerMainWindowZoomEditor) -> None:
        super().__init__(mw)
        self.ctx = ctx
        self.mw = mw
        self.simple_actions = simple_actions
        self.annotation_action_group = annotation_action_group
        self.zoom_action_group = zoom_action_group
        self.zoom_action_group.zoomActionsChanged.connect(self.on_zoom_actions_changed)
        self.zoom_editor = zoom_editor
        self.init_actions()
        self.layout().setSpacing(5)
        self.setIconSize(QSize(24, 24))

    def init_actions(self):
        toolbar = self
        d = self.simple_actions.actions
        toolbar.addAction(d[ActionType.open])
        toolbar.addAction(d[ActionType.slide_properties])
        toolbar.addAction(d[ActionType.toggle_grid])
        toolbar.addAction(d[ActionType.take_screenshot])
        toolbar.addAction(d[ActionType.take_screenshot_to_clipboard])
        toolbar.addAction(SeparatorAction(self))
        toolbar.addActions(self.annotation_action_group.actions())
        toolbar.addAction(SeparatorAction(self))
        toolbar.addAction(d[ActionType.fit])

        toolbar.addWidget(self.zoom_editor)

    def on_zoom_actions_changed(self, actions, prev_actions):
        toolbar = self
        for action in prev_actions:
            toolbar.removeAction(action)
        for action in actions:
            toolbar.addAction(action)
