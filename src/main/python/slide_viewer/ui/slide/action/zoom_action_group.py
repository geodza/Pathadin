from typing import Optional, Callable, Dict

from PyQt5.QtCore import pyqtSignal, QObject
from PyQt5.QtGui import QFont, QTransform
from PyQt5.QtWidgets import QActionGroup
from dataclasses import dataclass, InitVar

from slide_viewer.common.slide_helper import SlideHelper
from common_qt.action.my_action import MyAction
from slide_viewer.ui.slide.callback.on_zoom import on_zoom
from slide_viewer.ui.slide.widget.interface.active_view_provider import ActiveViewProvider
from slide_viewer.ui.slide.widget.interface.mdi_sub_window_service import SubWindowService


def build_scale_zooms(slide_helper: SlideHelper) -> Dict[float, float]:
    scale_zooms = {}
    for downsample in slide_helper.level_downsamples:
        zoom = int(slide_helper.downsample_to_zoom(downsample))
        if zoom > 0:
            scale = slide_helper.zoom_to_scale(zoom)
            scale_zooms[scale] = zoom
    scale_zooms[slide_helper.zoom_to_scale(1)] = 1
    return scale_zooms


@dataclass
class ZoomActionGroup(QActionGroup):
    parent_: InitVar[Optional[QObject]]
    active_view_provider: InitVar[ActiveViewProvider]
    sub_window_service: InitVar[SubWindowService]

    zoomActionsChanged = pyqtSignal()

    def __post_init__(self, parent_: Optional[QObject], active_view_provider: ActiveViewProvider,
                      sub_window_service: SubWindowService):
        super().__init__(parent_)
        self.cleanup: Optional[Callable[[], None]] = None

        def view_closure_factory(scale):
            def f():
                view = active_view_provider.active_view
                on_zoom(view, scale)

            return f

        def on_sub_window_activated():
            if self.cleanup:
                self.cleanup()
                self.cleanup = None

            view = active_view_provider.active_view

            def cleanup():
                view.transformChanged.disconnect(on_scale_changed)
                self.clear_actions()

            # def on_scale_changed(scale: float):
            #     for scale_ in scale_actions:
            #         scales_are_close = 0.9 * scale_ < scale and scale < 1.1 * scale_
            #         scale_actions[scale_].setChecked(scales_are_close)

            def on_scale_changed(t: QTransform):
                scale = t.m11()
                for scale_ in scale_actions:
                    scales_are_close = 0.9 * scale_ < scale and scale < 1.1 * scale_
                    scale_actions[scale_].setChecked(scales_are_close)

                # action = scale_actions.get(scale)
                # if action:
                #     action.setChecked(True)
                # else:
                #     self.uncheck_actions()

            if view and view.slide_helper:
                self.cleanup = cleanup
                font = QFont()
                font.setPointSize(10)
                scale_zooms = build_scale_zooms(view.slide_helper)
                scale_actions = {}
                for scale, zoom in scale_zooms.items():
                    action_text = f"\u00D7{zoom}"
                    action = MyAction(action_text, self, view_closure_factory(scale))
                    action.setCheckable(True)
                    action.setFont(font)
                    self.addAction(action)
                    scale_actions[scale] = action
                self.zoomActionsChanged.emit()
                view.transformChanged.connect(on_scale_changed)
            else:
                self.clear_actions()

        # TODO does slideChange causes sub_window_activated? If not, we need to connect to slideChange too
        sub_window_service.sub_window_activated.connect(on_sub_window_activated)

    def clear_actions(self) -> None:
        for action in self.actions():
            self.removeAction(action)
        self.zoomActionsChanged.emit()

    def uncheck_actions(self) -> None:
        for action in self.actions():
            action.setChecked(False)
