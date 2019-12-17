from enum import Enum, unique, auto
from typing import Dict

from PyQt5.QtCore import QObject
from dataclasses import dataclass, InitVar

from slide_viewer.ui.common.action.my_action import MyAction
from slide_viewer.ui.common.disability.decorator import subscribe_disableable
from slide_viewer.ui.slide.callback.on_copy_screenshot import on_copy_screenshot
from slide_viewer.ui.slide.callback.on_export_annotations import on_export_annotations
from slide_viewer.ui.slide.callback.on_fit import on_fit
from slide_viewer.ui.slide.callback.on_grid_change_size import on_grid_change_size
from slide_viewer.ui.slide.callback.on_grid_toggle import on_grid_toggle
from slide_viewer.ui.slide.callback.on_import_annotations import on_import_annotations
from slide_viewer.ui.slide.callback.on_open_image_file import on_open_image_file
from slide_viewer.ui.slide.callback.on_save_screenshot import on_save_screenshot
from slide_viewer.ui.slide.callback.on_select_view_background_color import on_select_view_background_color
from slide_viewer.ui.slide.callback.on_show_image_properties import on_show_image_properties
from slide_viewer.ui.slide.callback.sub_window.on_add_sub_window import on_add_sub_window
from slide_viewer.ui.slide.callback.sub_window.on_tile_sub_windows import on_tile_sub_windows
from slide_viewer.ui.slide.widget.icons import IconName
from slide_viewer.ui.slide.widget.interface.active_annotation_tree_view_provider import ActiveAnnotationTreeViewProvider
from slide_viewer.ui.slide.widget.interface.active_view_provider import ActiveViewProvider
from slide_viewer.ui.slide.widget.interface.icon_provider import IconProvider
from slide_viewer.ui.slide.widget.interface.mdi_sub_window_service import SubWindowService


@unique
class ActionType(Enum):
    toggle_grid = auto()
    change_grid_size = auto()
    take_screenshot = auto()
    take_screenshot_to_clipboard = auto()
    slide_properties = auto()
    view_background_color = auto()
    open = auto()
    fit = auto()
    export_annotations = auto()
    import_annotations = auto()
    add_sub_window = auto()
    tile_sub_windows = auto()


action_type_to_title: Dict[ActionType, IconName] = {
    ActionType.toggle_grid: "Toggle &grid",
    ActionType.change_grid_size: "Grid si&ze",
    ActionType.take_screenshot: "&Save screenshot",
    ActionType.take_screenshot_to_clipboard: "&Copy screenshot to clipboard",
    ActionType.slide_properties: "Show &properties",
    ActionType.view_background_color: "&Background color",
    ActionType.open: "&Open image",
    ActionType.fit: "&Fit",
    ActionType.export_annotations: "&Export annotations",
    ActionType.import_annotations: "&Import annotations",
    ActionType.add_sub_window: "&Add subwindow",
    ActionType.tile_sub_windows: "&Tile subwindows",
}

action_type_to_icon_name: Dict[ActionType, IconName] = {
    ActionType.toggle_grid: IconName.grid_on,
    ActionType.change_grid_size: None,
    ActionType.take_screenshot: IconName.photo_camera,
    ActionType.take_screenshot_to_clipboard: IconName.camera,
    ActionType.slide_properties: IconName.description,
    ActionType.view_background_color: IconName.color_lens,
    ActionType.open: IconName.folder_open,
    ActionType.fit: IconName.zoom_out_map,
    ActionType.export_annotations: None,
    ActionType.import_annotations: None,
    ActionType.add_sub_window: IconName.add_to_queue,
    ActionType.tile_sub_windows: IconName.view_module,
}


@dataclass
class SimpleActions:
    parent_: InitVar[QObject]
    active_view_provider: InitVar[ActiveViewProvider]
    active_annotation_tree_view_provider: InitVar[ActiveAnnotationTreeViewProvider]
    sub_window_service: InitVar[SubWindowService]
    icon_provider: InitVar[IconProvider]

    def __post_init__(self, parent_: QObject, active_view_provider: ActiveViewProvider,
                      active_annotation_tree_view_provider: ActiveAnnotationTreeViewProvider,
                      sub_window_service: SubWindowService, icon_provider: IconProvider):
        def view_closure(func, checkable=False):
            def f(checked: bool):
                view = active_view_provider.active_view
                if checkable:
                    func(view, checked)
                else:
                    func(view)

            return f

        def annotations_tree_view_closure(func):
            def f(checked: bool):
                view = active_view_provider.active_view
                annotations_tree_view = active_annotation_tree_view_provider.active_annotation_tree_view
                func(annotations_tree_view, view.slide_helper.slide_path)

            return f

        def annotation_service_closure(func):
            def f(checked: bool):
                view = active_view_provider.active_view
                annotation_service = view.annotation_service
                func(annotation_service, view.slide_helper.slide_path)

            return f

        def sub_window_service_closure(func, checkable=False):
            def f(checked: bool):
                if checkable:
                    func(sub_window_service, checked)
                else:
                    func(sub_window_service)

            return f

        callbacks = {
            ActionType.toggle_grid: view_closure(on_grid_toggle, True),
            ActionType.change_grid_size: view_closure(on_grid_change_size),
            ActionType.take_screenshot: view_closure(on_save_screenshot),
            ActionType.take_screenshot_to_clipboard: view_closure(on_copy_screenshot),
            ActionType.slide_properties: view_closure(on_show_image_properties),
            ActionType.view_background_color: view_closure(on_select_view_background_color),
            ActionType.open: view_closure(on_open_image_file),
            ActionType.fit: view_closure(on_fit),
            ActionType.export_annotations: annotation_service_closure(on_export_annotations),
            ActionType.import_annotations: annotation_service_closure(on_import_annotations),
            ActionType.add_sub_window: sub_window_service_closure(on_add_sub_window),
            ActionType.tile_sub_windows: sub_window_service_closure(on_tile_sub_windows),
        }

        def are_sub_windows_present() -> bool:
            return sub_window_service.has_sub_windows

        def is_active_view_present() -> bool:
            view = active_view_provider.active_view
            return view is not None

        def is_active_view_with_slide_helper() -> bool:
            view = active_view_provider.active_view
            return view is not None and view.slide_helper is not None

        actions = {}
        for action_type in ActionType:
            actions[action_type] = MyAction(action_type_to_title[action_type], parent_,
                                            callbacks.get(action_type, None),
                                            icon_provider.get_icon(action_type_to_icon_name[action_type]))

        for action_type in ActionType:
            action = actions[action_type]
            if action_type in [ActionType.toggle_grid]:
                action.setCheckable(True)

            if action_type in [ActionType.open]:
                action.setDisabled(True)
                subscribe_disableable([sub_window_service.sub_window_activated], is_active_view_present,
                                      action)
            elif action_type in [ActionType.tile_sub_windows]:
                action.setDisabled(True)
                subscribe_disableable([sub_window_service.sub_window_activated], are_sub_windows_present,
                                      action)
            elif action_type in [ActionType.add_sub_window]:
                pass
            else:
                action.setDisabled(True)
                subscribe_disableable([sub_window_service.sub_window_activated], is_active_view_with_slide_helper,
                                      action)

        def sub_window_activated():
            view = active_view_provider.active_view
            # actions[ActionType.sync_all].setChecked(sub_window_service.is_sync)
            if view:
                a = actions[ActionType.toggle_grid]
                a.setChecked(view.get_grid_visible())

        sub_window_service.sub_window_activated.connect(sub_window_activated)

        self.actions = actions
