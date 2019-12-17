from typing import Optional, Callable, Dict

from PyQt5.QtCore import QObject
from PyQt5.QtWidgets import QActionGroup, QAction
from dataclasses import InitVar, dataclass

from slide_viewer.ui.common.action.my_action import MyAction
from slide_viewer.ui.common.disability.decorator import subscribe_disableable
from slide_viewer.ui.model.annotation_type import AnnotationType
from slide_viewer.ui.slide.callback.on_annotation_item import on_annotation_item, on_selection_tool
from slide_viewer.ui.slide.widget.interface.active_view_provider import ActiveViewProvider
from slide_viewer.ui.slide.widget.interface.icon_provider import IconProvider
from slide_viewer.ui.slide.widget.icons import IconName
from slide_viewer.ui.slide.widget.interface.mdi_sub_window_service import SubWindowService


@dataclass
class AnnotationActionGroup(QActionGroup):
    parent_: InitVar[Optional[QObject]]
    active_view_provider: InitVar[ActiveViewProvider]
    sub_window_service: InitVar[SubWindowService]
    icon_provider: InitVar[IconProvider]

    def __post_init__(self, parent_: Optional[QObject], active_view_provider: ActiveViewProvider,
                      sub_window_service: SubWindowService, icon_provider: IconProvider):
        super().__init__(parent_)
        self.cleanup: Optional[Callable[[], None]] = None

        def pan_closure():
            def f():
                on_selection_tool(active_view_provider.active_view)

            return f

        def annotation_item_closure(annotation_type: AnnotationType):
            def f():
                on_annotation_item(active_view_provider.active_view, annotation_type)

            return f

        a1 = MyAction("&Pan/select tool", self, pan_closure(), icon_provider.get_icon(IconName.pan_tool))
        a2 = MyAction("&Line annotation", self, annotation_item_closure(AnnotationType.LINE),
                      icon_provider.get_icon(IconName.line))
        a3 = MyAction("&Rect annotation", self, annotation_item_closure(AnnotationType.RECT),
                      icon_provider.get_icon(IconName.rect))
        a4 = MyAction("&Ellipse annotation", self, annotation_item_closure(AnnotationType.ELLIPSE),
                      icon_provider.get_icon(IconName.ellipse))
        a5 = MyAction("&Polygon annotation. Press Enter to close current polygon", self,
                      annotation_item_closure(AnnotationType.POLYGON), icon_provider.get_icon(IconName.polygon))

        d: Dict[AnnotationType, QAction] = {
            None: a1,
            AnnotationType.LINE: a2,
            AnnotationType.RECT: a3,
            AnnotationType.ELLIPSE: a4,
            AnnotationType.POLYGON: a5,
        }

        def is_active_view_with_slide_helper() -> bool:
            view = active_view_provider.active_view
            return view is not None and view.slide_helper is not None

        for action in self.actions():
            action.setCheckable(True)
            subscribe_disableable([sub_window_service.sub_window_activated], is_active_view_with_slide_helper, action)

        def on_sub_window_activated():
            if self.cleanup:
                self.cleanup()
                self.cleanup = None

            def cleanup():
                for action in self.actions():
                    action.setChecked(False)

            view = active_view_provider.active_view
            if view and view.slide_helper:
                self.setDisabled(False)
                active_action = d[view.annotation_type]
                active_action.setChecked(True)
                self.cleanup = cleanup
            else:
                self.setDisabled(True)

        sub_window_service.sub_window_activated.connect(on_sub_window_activated)
