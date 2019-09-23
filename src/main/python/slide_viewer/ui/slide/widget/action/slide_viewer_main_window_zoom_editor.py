from PyQt5.QtWidgets import QAction, QPushButton, QToolBar, QLineEdit, QMenu, QWidget, QHBoxLayout, QLayout


class SlideViewerMainWindowZoomEditor(QWidget):

    def __init__(self, mw, ctx) -> None:
        super().__init__(mw)
        self.ctx = ctx
        self.mw = mw
        self.mw.slide_viewer_widget.view.scaleChanged.connect(self.on_view_scale_changed)
        self.zoom_line_edit = QLineEdit()
        self.zoom_line_edit.returnPressed.connect(self.on_zoom_line_edit_pressed)
        self.zoom_line_edit.setMaximumWidth(50)
        layout = QHBoxLayout()
        layout.setSizeConstraint(QLayout.SetFixedSize)
        self.setLayout(layout)
        self.layout().addWidget(self.zoom_line_edit)
        button = QPushButton(self.ctx.icon_magnifier, None, self)
        button.clicked.connect(self.on_zoom_line_edit_pressed)
        self.layout().addWidget(button)

    def on_view_scale_changed(self, scale):
        slide_helper = self.mw.slide_viewer_widget.slide_helper
        if not slide_helper:
            return
        # self.zoom_line_edit.setText("{:.4F}".format(new_scale))
        zoom = slide_helper.scale_to_zoom(scale)
        # print(f"new_scale: {scale}, new_zoom: {zoom}")
        self.zoom_line_edit.setText("{:.2f}".format(zoom))

    def on_zoom_line_edit_pressed(self):
        slide_helper = self.mw.slide_viewer_widget.slide_helper
        if not slide_helper:
            return
        try:
            zoom = float(self.zoom_line_edit.text())
            scale = slide_helper.zoom_to_scale(zoom)
            self.mw.slide_viewer_widget.view.set_scale_in_view_center(scale)
        except:
            pass
