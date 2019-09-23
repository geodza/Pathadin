from enum import Enum, unique

from slide_viewer.ui.common.closure_factory import closure_factory
from slide_viewer.ui.common.my_action import MyAction
from slide_viewer.ui.slide.widget.action.callback.on_copy_screenshot import on_copy_screenshot
from slide_viewer.ui.slide.widget.action.callback.on_export_annotations import on_export_annotations
from slide_viewer.ui.slide.widget.action.callback.on_fit import on_fit
from slide_viewer.ui.slide.widget.action.callback.on_grid_change_size import on_grid_change_size
from slide_viewer.ui.slide.widget.action.callback.on_grid_toggle import on_grid_toggle
from slide_viewer.ui.slide.widget.action.callback.on_import_annotations import on_import_annotations
from slide_viewer.ui.slide.widget.action.callback.on_open_image_file import on_open_image_file
from slide_viewer.ui.slide.widget.action.callback.on_save_screenshot import on_save_screenshot
from slide_viewer.ui.slide.widget.action.callback.on_select_view_background_color import on_select_view_background_color
from slide_viewer.ui.slide.widget.action.callback.on_show_image_properties import on_show_image_properties


@unique
class ActionType(Enum):
    toggle_grid = 1
    change_grid_size = 2
    take_screenshot = 3
    take_screenshot_to_clipboard = 4
    slide_properties = 5
    view_background_color = 6
    open = 7
    fit = 8
    export_annotations = 9
    import_annotations = 10


class MainWindowSimpleActions:

    def __init__(self, mw, ctx) -> None:
        super().__init__()
        self.ctx = ctx
        self.mw = mw
        self.titles = {}
        self.icons = {}
        self.callbacks = {}
        self.actions = {}
        self.update_titles()
        self.update_icons()
        self.update_callbacks()
        self.update_actions()

    def update_titles(self):
        d = self.titles
        d[ActionType.toggle_grid] = "Toggle &grid"
        d[ActionType.change_grid_size] = "Grid &size"
        d[ActionType.take_screenshot] = "&Save screenshot"
        d[ActionType.take_screenshot_to_clipboard] = "&Copy screenshot to clipboard"
        d[ActionType.slide_properties] = "Show &properties"
        d[ActionType.view_background_color] = "&Background color"
        d[ActionType.open] = "&Open image"
        d[ActionType.fit] = "&Fit"
        d[ActionType.export_annotations] = "&Export annotations"
        d[ActionType.import_annotations] = "&Import annotations"

    def update_icons(self):
        d = self.icons
        d[ActionType.toggle_grid] = self.ctx.icon_grid
        d[ActionType.change_grid_size] = None
        d[ActionType.take_screenshot] = self.ctx.icon_screenshot
        d[ActionType.take_screenshot_to_clipboard] = self.ctx.icon_camera
        d[ActionType.slide_properties] = self.ctx.icon_description
        d[ActionType.view_background_color] = self.ctx.icon_palette
        d[ActionType.open] = self.ctx.icon_open
        d[ActionType.fit] = self.ctx.icon_fit
        d[ActionType.export_annotations] = None
        d[ActionType.import_annotations] = None

    def update_callbacks(self):
        d = self.callbacks

        def grid_closure(func):
            def wrap_():
                func(self.mw.slide_viewer_widget.slide_graphics_grid_item)

            return wrap_

        def widget_closure(func):
            def wrap_():
                func(self.mw.slide_viewer_widget)

            return wrap_

        widget = self.mw.slide_viewer_widget
        d[ActionType.toggle_grid] = grid_closure(on_grid_toggle)
        d[ActionType.change_grid_size] = grid_closure(on_grid_change_size)
        d[ActionType.take_screenshot] = widget_closure(on_save_screenshot)
        d[ActionType.take_screenshot_to_clipboard] = closure_factory(widget.view)(on_copy_screenshot)
        d[ActionType.slide_properties] = widget_closure(on_show_image_properties)
        d[ActionType.view_background_color] = closure_factory(widget.view)(on_select_view_background_color)
        d[ActionType.open] = widget_closure(on_open_image_file)
        d[ActionType.fit] = closure_factory(widget.view)(on_fit)
        d[ActionType.export_annotations] = widget_closure(on_export_annotations)
        d[ActionType.import_annotations] = widget_closure(on_import_annotations)

    def update_actions(self):
        d = self.actions
        for action_type in self.titles:
            d[action_type] = MyAction(self.titles[action_type], self.mw, self.callbacks.get(action_type, None),
                                      self.icons[action_type])
