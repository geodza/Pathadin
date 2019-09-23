from PyQt5.QtWidgets import QActionGroup

from slide_viewer.ui.common.my_action import MyAction
from slide_viewer.ui.common.closure_factory import closure_factory
from slide_viewer.ui.slide.graphics.annotation.annotation_type import AnnotationType
from slide_viewer.ui.slide.widget.action.callback.annotation_item import on_annotation_item, on_selection_tool


class MainWindowAnnotationActionGroup(QActionGroup):
    def __init__(self, mw, ctx) -> None:
        super().__init__(mw)
        self.ctx = ctx
        self.mw = mw
        widget = self.mw.slide_viewer_widget
        pan_tool = MyAction("&Pan/select tool", self, closure_factory(widget)(on_selection_tool), ctx.icon_pan_tool)
        pan_tool.setChecked(True)
        MyAction("&Line annotation", self, closure_factory(widget, AnnotationType.LINE)(on_annotation_item),
                 self.ctx.icon_line)
        MyAction("&Rect annotation", self, closure_factory(widget, AnnotationType.RECT)(on_annotation_item),
                 self.ctx.icon_rect)
        MyAction("&Ellipse annotation", self, closure_factory(widget, AnnotationType.ELLIPSE)(on_annotation_item),
                 self.ctx.icon_ellipse)
        MyAction("&Polygon annotation. Press Enter to close current polygon", self,
                 closure_factory(widget, AnnotationType.POLYGON)(on_annotation_item), self.ctx.icon_polygon)

        for action in self.actions():
            action.setCheckable(True)
