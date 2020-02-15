from typing import Optional, Callable

from PyQt5.QtCore import QMargins, QObject
from PyQt5.QtGui import QTransform
from PyQt5.QtWidgets import QWidget, QHBoxLayout, QDoubleSpinBox
from dataclasses import dataclass, InitVar

from common_qt.slot_disconnected_utils import slot_disconnected
from slide_viewer.ui.slide.widget.interface.active_view_provider import ActiveViewProvider
from slide_viewer.ui.slide.widget.interface.mdi_sub_window_service import SubWindowService


@dataclass
class ZoomEditor(QWidget):
    parent_: InitVar[Optional[QObject]]
    active_view_provider: InitVar[ActiveViewProvider]
    sub_window_service: InitVar[SubWindowService]
    single_step_zoom: InitVar[float] = 0.05

    def __post_init__(self, parent_: Optional[QObject], active_view_provider: ActiveViewProvider,
                      sub_window_service: SubWindowService, single_step_zoom: float):
        super().__init__(parent_)
        self.manual_zoom_input = QDoubleSpinBox()
        self.manual_zoom_input.setSingleStep(single_step_zoom)
        self.manual_zoom_input.setDisabled(True)
        layout = QHBoxLayout()
        layout.setContentsMargins(QMargins())
        self.setLayout(layout)
        layout.addWidget(self.manual_zoom_input)
        self.cleanup: Optional[Callable] = None

        def on_view_changed():
            if self.cleanup:
                self.cleanup()
                self.cleanup = None

            view = active_view_provider.active_view

            def cleanup():
                self.manual_zoom_input.valueChanged.disconnect(on_zoom_change)
                view.transformChanged.disconnect(on_scale_change)

            if view and view.slide_helper:
                def on_scale_change(t: QTransform):
                    scale = t.m11()
                    with slot_disconnected(self.manual_zoom_input.valueChanged, on_zoom_change):
                        zoom = view.slide_helper.scale_to_zoom(scale)
                        self.manual_zoom_input.setValue(zoom)

                def on_zoom_change(zoom: float):
                    with slot_disconnected(view.transformChanged, on_scale_change):
                        scale = view.slide_helper.zoom_to_scale(zoom)
                        view.set_scale_in_view_center(scale)
                        # calling on_scale_change because view can limit passed scale to another value
                        on_scale_change(view.transform())

                self.manual_zoom_input.valueChanged.connect(on_zoom_change)
                view.transformChanged.connect(on_scale_change)
                self.cleanup = cleanup
                self.manual_zoom_input.setDisabled(False)
                on_scale_change(view.transform())
            else:
                self.manual_zoom_input.setDisabled(True)
                self.manual_zoom_input.clear()

        sub_window_service.sub_window_activated.connect(on_view_changed)
