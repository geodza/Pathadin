from enum import Enum, unique

from PyQt5.QtWidgets import QMenu, QMenuBar

from slide_viewer.ui.common.separator_action import SeparatorAction
from slide_viewer.ui.slide.widget.action.slide_viewer_main_window_simple_actions import MainWindowSimpleActions, \
    ActionType
from slide_viewer.ui.slide.widget.action.slide_viewer_main_window_annotation_action_group import \
    MainWindowAnnotationActionGroup
from slide_viewer.ui.slide.widget.action.slide_viewer_main_window_zoom_action_group import MainWindowZoomActionGroup


@unique
class MenuType(Enum):
    actions = 1
    zoom = 2
    grid = 3
    annotations = 4


class SlideViewerMainWindowMenubar(QMenuBar):

    def __init__(self, mw, ctx, simple_actions: MainWindowSimpleActions,
                 zoom_action_group: MainWindowZoomActionGroup,
                 annotation_action_group: MainWindowAnnotationActionGroup) -> None:
        super().__init__(mw)
        self.mw = mw
        self.ctx = ctx
        self.simple_actions = simple_actions
        self.annotation_action_group = annotation_action_group
        self.zoom_action_group = zoom_action_group
        self.zoom_action_group.zoomActionsChanged.connect(self.on_zoom_actions_changed)
        self.menu_titles = {}
        self.menu_action_types = {}
        self.menu_actions = {}
        self.menus = {}
        self.init_menu_titles()
        # self.init_menu_action_types()
        self.init_menu_actions()
        self.init_menus()
        self.init_menu_bar()

    def init_menu_titles(self):
        d = self.menu_titles
        d[MenuType.actions] = "Actions"
        d[MenuType.zoom] = "Zoom"
        d[MenuType.grid] = "Grid"
        d[MenuType.annotations] = "Annotations"

    def init_menu_actions(self):
        d = self.menu_actions
        a = self.simple_actions.actions
        d[MenuType.actions] = [a[ActionType.open], a[ActionType.slide_properties], a[ActionType.take_screenshot],
                               a[ActionType.take_screenshot_to_clipboard], a[ActionType.view_background_color],
                               a[ActionType.export_annotations], a[ActionType.import_annotations]]
        d[MenuType.zoom] = [a[ActionType.fit], SeparatorAction(self), *self.zoom_action_group.actions()]
        d[MenuType.grid] = [a[ActionType.toggle_grid], a[ActionType.change_grid_size]]
        d[MenuType.annotations] = [*self.annotation_action_group.actions()]

    def init_menus(self):
        d = self.menus
        for menu_type in self.menu_titles:
            d[menu_type] = QMenu(self.menu_titles[menu_type], self.mw)
            # for action_type in self.menu_action_types[menu_type]:
            for action in self.menu_actions[menu_type]:
                # action = self.simple_actions.actions[action_type]
                d[menu_type].addAction(action)

    def init_menu_bar(self):
        d = self.menus
        menubar = self
        menubar.addMenu(d[MenuType.actions])
        menubar.addMenu(d[MenuType.zoom])
        menubar.addMenu(d[MenuType.annotations])
        menubar.addMenu(d[MenuType.grid])

    def on_zoom_actions_changed(self, actions, prev_actions):
        self.menu_actions[MenuType.zoom] = [self.simple_actions.actions[ActionType.fit], SeparatorAction(self), actions]
        zoom_menu = self.menus[MenuType.zoom]
        for action in prev_actions:
            zoom_menu.removeAction(action)
        for action in actions:
            zoom_menu.addAction(action)
