from collections import OrderedDict
from PyQt5.QtCore import pyqtSignal
from PyQt5.QtGui import QFont
from PyQt5.QtWidgets import QActionGroup

from slide_viewer.ui.common.my_action import MyAction
from slide_viewer.ui.slide.widget.action.callback.on_zoom import on_zoom
from slide_viewer.ui.common.closure_factory import closure_factory


class MainWindowZoomActionGroup(QActionGroup):
    zoomActionsChanged = pyqtSignal(list, list)

    def __init__(self, mw, ctx) -> None:
        super().__init__(mw)
        self.ctx = ctx
        self.mw = mw
        self.mw.slide_viewer_widget.slideFileChanged.connect(self.on_slide_change)
        self.mw.slide_viewer_widget.view.scaleChanged.connect(self.on_view_scale_changed)
        self.scale_zooms = {}
        self.scale_actions = OrderedDict()
        self.init_()

    def init_(self):
        self.init_scale_zooms()
        self.init_scale_actions()
        self.init_scale_action_group()

    def init_scale_zooms(self):
        slide_helper = self.mw.slide_viewer_widget.slide_helper
        if not slide_helper:
            return

        self.scale_zooms.clear()
        for downsample in slide_helper.level_downsamples:
            zoom = int(slide_helper.downsample_to_zoom(downsample))
            if zoom > 0:
                scale = 1 / downsample
                self.scale_zooms[scale] = zoom
        # print(self.scale_zooms)

    def init_scale_actions(self):
        slide_helper = self.mw.slide_viewer_widget.slide_helper
        if not slide_helper:
            return
        self.scale_actions.clear()
        widget = self.mw.slide_viewer_widget
        default_font = QFont()
        default_font.setPointSize(12)
        for scale, ui_zoom in self.scale_zooms.items():
            action_text = "x{}".format(ui_zoom)
            scale_action = MyAction(action_text, self.mw, closure_factory(widget.view, scale)(on_zoom))
            scale_action.setCheckable(True)
            scale_action.setFont(default_font)
            self.scale_actions[scale] = scale_action

    def init_scale_action_group(self):
        # self.zoom_actions = zoom_actions
        # previous_zoom_actions = self.zoom_actions
        previous_zoom_actions = self.actions()
        for action in previous_zoom_actions:
            self.removeAction(action)
        for action in self.scale_actions.values():
            self.addAction(action)
        self.zoomActionsChanged.emit(self.actions(), previous_zoom_actions)

    def on_slide_change(self):
        self.init_()

    def on_view_scale_changed(self, scale):
        for scale_ in self.scale_actions:
            scales_are_equal = 0.9 * scale_ < scale and scale < 1.1 * scale_
            self.scale_actions[scale_].setChecked(scales_are_equal)
