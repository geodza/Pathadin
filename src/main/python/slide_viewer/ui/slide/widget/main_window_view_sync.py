from typing import List, Dict, Callable

from slide_viewer.ui.slide.graphics.view.graphics_view import GraphicsView
from slide_viewer.ui.slide.widget.interface.mdi_sub_window_service import SyncOption


def setup_sync(view: GraphicsView, sub_views_except_active: List[GraphicsView], sync_states: Dict[SyncOption, bool]) \
        -> Callable[[], None]:
    def cleanup():
        view.setDisabled(True)
        # print(f'cleanup --------------')
        # print(f'cleanup {id(view)}')
        for sub_view in sub_views_except_active:
            if sync_states.get(SyncOption.view_transform):
                # pass
                view.transformChanged.disconnect(sub_view.setTransform)
                view.viewUpdated.disconnect(sub_view.update)
                view.viewSceneRectUpdated.disconnect(sub_view.updateSceneRect)
                view.viewSceneRectsUpdated.disconnect(sub_view.updateScene)
            if sync_states.get(SyncOption.grid_visible):
                view.gridVisibleChanged.disconnect(sub_view.set_grid_visible)
            if sync_states.get(SyncOption.grid_size):
                view.gridSizeChanged.disconnect(sub_view.set_grid_size)
                view.gridSizeIsInPixelsChanged.disconnect(sub_view.set_grid_size_is_in_pixels)
            if sync_states.get(SyncOption.file_path):
                view.filePathChanged.disconnect(sub_view.set_file_path)
            if sync_states.get(SyncOption.background_brush):
                view.backgroundBrushChanged.disconnect(sub_view.set_background_brush)
            if sync_states.get(SyncOption.annotations):
                view.annotation_service.added_signal().disconnect(sub_view.annotation_service.add_copy)
                view.annotation_service.deleted_signal().disconnect(sub_view.annotation_service.delete_if_exist)
                view.scene().annotationModelsSelected.disconnect(sub_view.scene().select_annotations)
                # try:
                if sync_states.get(SyncOption.annotation_filter):
                    view.annotation_service.edited_signal().disconnect(sub_view.annotation_service.add_or_edit_with_copy)
                else:
                    view.annotation_service.edited_signal().disconnect(sub_view.annotation_service.add_or_edit_with_copy_without_filter)
                # except:
                #     pass

    for sub_view in sub_views_except_active:
        if sync_states.get(SyncOption.view_transform):
            # pass
            view.transformChanged.connect(sub_view.setTransform)
            view.viewUpdated.connect(sub_view.update)
            view.viewSceneRectUpdated.connect(sub_view.updateSceneRect)
            view.viewSceneRectsUpdated.connect(sub_view.updateScene)
        if sync_states.get(SyncOption.grid_visible):
            view.gridVisibleChanged.connect(sub_view.set_grid_visible)
        if sync_states.get(SyncOption.grid_size):
            view.gridSizeChanged.connect(sub_view.set_grid_size)
            view.gridSizeIsInPixelsChanged.connect(sub_view.set_grid_size_is_in_pixels)
        if sync_states.get(SyncOption.file_path):
            view.filePathChanged.connect(sub_view.set_file_path)
        if sync_states.get(SyncOption.background_brush):
            view.backgroundBrushChanged.connect(sub_view.set_background_brush)
        if sync_states.get(SyncOption.annotations):
            # view.annotation_service.added_signal().connect(sub_view.annotation_service.add_copy, type=Qt.QueuedConnection)
            view.annotation_service.added_signal().connect(sub_view.annotation_service.add_copy)
            view.annotation_service.deleted_signal().connect(sub_view.annotation_service.delete_if_exist)
            view.scene().annotationModelsSelected.connect(sub_view.scene().select_annotations)
            if sync_states.get(SyncOption.annotation_filter):
                # view.annotation_service.edited_signal().connect(sub_view.annotation_service.add_or_edit_with_copy, type=Qt.QueuedConnection)
                view.annotation_service.edited_signal().connect(sub_view.annotation_service.add_or_edit_with_copy)
                # view.annotation_service.edited_signal().connect(debounce_slot(0.01, sub_view.annotation_service.add_or_edit_with_copy))
            else:
                view.annotation_service.edited_signal().connect(sub_view.annotation_service.add_or_edit_with_copy_without_filter)
    view.setDisabled(False)
    return cleanup
