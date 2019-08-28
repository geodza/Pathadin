from PyQt5.QtGui import QPixmapCache, QPixmap, QIcon, QCloseEvent, QImageReader, QImage, QPainter
from PyQt5.QtSvg import QSvgRenderer
from PyQt5.QtWidgets import QMainWindow, QWidget, QVBoxLayout, QLineEdit, QPushButton, QAction, QLabel, QDialog, \
    QSpinBox, QHBoxLayout, QFormLayout, QDialogButtonBox, QColorDialog, QApplication, QWidgetAction
from PyQt5.QtCore import Qt, QSize, QSettings
from PyQt5.QtGui import QBrush, QPen, QColor, QPixmapCache, QTransform

from slide_viewer.config import debug, initial_main_window_size, initial_scene_background_color
from slide_viewer.my_action import MyAction
from slide_viewer.my_menu import MyMenu
from slide_viewer.on_load_slide_action import SelectSlideFileAction
from slide_viewer.screenshot_builders import build_screenshot_image_from_view
from slide_viewer.slide_helper import SlideHelper
from slide_viewer.slide_viewer_widget import SlideViewerWidget
from slide_viewer.select_image_file_action import SelectImageFileAction


class SlideViewerMainWindow(QMainWindow):

    def __init__(self, ctx):
        super().__init__()
        self.ctx = ctx
        self.text = None
        self.debug = debug
        self.dynamic_zoom_actions = []

        widget = QWidget(self)
        layout = QVBoxLayout(widget)
        self.slide_viewer_widget = SlideViewerWidget(widget, self.on_load_slide_callback)
        self.slide_viewer_widget.view.zoomChanged.connect(self.on_view_zoom_changed)
        self.slide_viewer_widget.slideFileChanged.connect(self.on_slide_file_changed)
        layout.addWidget(self.slide_viewer_widget)
        widget.setLayout(layout)
        self.setCentralWidget(widget)

        self.main_toolbar = self.addToolBar("main_toolbar")
        self.main_toolbar.layout().setSpacing(5)
        self.main_toolbar.setIconSize(QSize(24, 24))

        menuBar = self.menuBar()
        self.actions_menu = MyMenu("actions", menuBar)
        menuBar.addMenu(self.actions_menu)
        # zoom_menu is dynamically populated in on_select_slide_file_action
        self.zoom_menu = MyMenu("zoom", menuBar)
        menuBar.addMenu(self.zoom_menu)
        self.grid_menu = MyMenu("grid", menuBar)
        menuBar.addMenu(self.grid_menu)

        self.select_slide_file_action = SelectSlideFileAction("&load", self.actions_menu,
                                                              self.on_select_slide_file_action, self.ctx.icon_open)
        self.main_toolbar.addAction(self.select_slide_file_action)

        self.grid_toggle_action = MyAction("toggle &grid", self.grid_menu, self.on_grid_toggle, self.ctx.icon_grid)
        self.main_toolbar.addAction(self.grid_toggle_action)

        self.grid_change_size_action = MyAction("grid &size", self.grid_menu, self.on_grid_change_size_action)

        self.take_screenshot_action = MyAction("&take screenshot", self.actions_menu, self.on_take_screenshot_action,
                                               self.ctx.icon_screenshot)
        self.main_toolbar.addAction(self.take_screenshot_action)

        self.select_background_color_action = MyAction("&background color", self.actions_menu,
                                                       self.on_select_background_color_action, self.ctx.icon_palette)
        self.add_dynamic_command()

        self.fit_action = MyAction("&fit", self.zoom_menu, None, self.ctx.icon_fit, "fit")
        self.main_toolbar.addAction(self.fit_action)

        self.zoom_action = MyAction("zoom", self, self.on_zoom_line_edit_pressed, self.ctx.icon_magnifier)
        self.main_toolbar.addAction(self.zoom_action)
        self.zoom_menu.triggered.connect(self.on_zoom_menu_action)

        self.zoom_line_edit = QLineEdit()
        self.zoom_line_edit.returnPressed.connect(self.on_zoom_line_edit_pressed)
        self.zoom_line_edit.setMaximumWidth(50)
        self.main_toolbar.addWidget(self.zoom_line_edit)

        self.read_settings()

    def on_view_zoom_changed(self, new_zoom):
        # self.zoom_line_edit.setText("{:.4F}".format(new_zoom))
        self.zoom_line_edit.setText("{:.1f}".format(1 / new_zoom))

    def on_slide_file_changed(self, new_slide_file):
        self.update_dynamic_zoom_actions(new_slide_file)

    def on_select_slide_file_action(self, file_path):
        self.slide_viewer_widget.load(file_path)

    def update_dynamic_zoom_actions(self, file_path):
        for action in self.dynamic_zoom_actions:
            self.zoom_menu.removeAction(action)
            self.main_toolbar.removeAction(action)
        self.dynamic_zoom_actions = []
        slide_helper = SlideHelper(file_path)
        for downsample in slide_helper.level_downsamples:
            downsample_action = MyAction(str(downsample), self.zoom_menu, None, None, downsample)
            f = downsample_action.font()
            f.setPointSize(11)
            downsample_action.setFont(f)
            self.dynamic_zoom_actions.append(downsample_action)
            self.zoom_menu.addAction(downsample_action)
            self.main_toolbar.addAction(downsample_action)

    def on_zoom_menu_action(self, action: QAction):
        if action.text() != "&fit":
            downsample = action.data()
            zoom = 1 / downsample
            self.slide_viewer_widget.view.set_zoom_in_view_center(zoom)
        else:
            self.slide_viewer_widget.view.fit_scene()

    def on_load_slide_callback(self):
        pass

    def on_grid_change_size_action(self):
        if not self.slide_viewer_widget.slide_graphics_grid_item:
            return
        dialog = QDialog()
        dialog.setWindowTitle("Grid size")
        grid_size = self.slide_viewer_widget.slide_graphics_grid_item.grid_size
        grid_w = QSpinBox()
        grid_w.setMaximum(2 ** 15)
        grid_w.setValue(grid_size[0])
        grid_h = QSpinBox()
        grid_h.setMaximum(2 ** 15)
        grid_h.setValue(grid_size[1])
        horizontal_layout = QHBoxLayout()
        horizontal_layout.addWidget(grid_w)
        horizontal_layout.addWidget(grid_h)
        form_layout = QFormLayout()
        form_layout.addRow("grid width:", horizontal_layout)

        main_layout = QVBoxLayout()
        main_layout.addLayout(form_layout)
        button_box = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel, dialog)
        main_layout.addWidget(button_box)
        dialog.setLayout(main_layout)
        button_box.accepted.connect(dialog.accept)
        button_box.rejected.connect(dialog.reject)
        res = dialog.exec()
        if res == QDialog.Accepted:
            self.slide_viewer_widget.slide_graphics_grid_item.grid_size = (grid_w.value(), grid_h.value())
            self.slide_viewer_widget.slide_graphics_grid_item.update_lines()

    def on_grid_toggle(self):
        if self.slide_viewer_widget.slide_graphics_grid_item:
            is_visible = self.slide_viewer_widget.slide_graphics_grid_item.isVisible()
            self.slide_viewer_widget.slide_graphics_grid_item.setVisible(not is_visible)

    def on_zoom_line_edit_pressed(self):
        try:
            zoom = float(self.zoom_line_edit.text())
            self.slide_viewer_widget.view.set_zoom_in_view_center(1 / zoom)
        except:
            pass

    def on_take_screenshot_action(self):
        def on_select_image_file(image_file: str):
            image = build_screenshot_image_from_view(self.slide_viewer_widget.view)
            image.save(image_file)

        if self.slide_viewer_widget.slide_graphics_grid_item:
            select_image_file_action = SelectImageFileAction("internal", self, on_select_image_file)
            select_image_file_action.trigger()

    def on_select_background_color_action(self):
        color_dialog = QColorDialog(Qt.white, self)
        color_dialog.setOptions(QColorDialog.ShowAlphaChannel)
        last_color = self.slide_viewer_widget.view.backgroundBrush().color()
        color_dialog.currentColorChanged.connect(self.on_background_color_change)
        color_dialog.colorSelected.connect(self.on_background_color_change)
        res = color_dialog.exec()
        if not res:
            self.slide_viewer_widget.view.setBackgroundBrush(last_color)

    def on_background_color_change(self, color):
        self.slide_viewer_widget.view.setBackgroundBrush(color)

    def write_settings(self):
        settings = QSettings("dieyepy", "dieyepy")
        settings.beginGroup("MainWindow");
        settings.setValue("size", self.size())
        settings.setValue("pos", self.pos())
        settings.setValue("background_color", self.slide_viewer_widget.view.backgroundBrush().color())
        settings.endGroup()

    def read_settings(self):
        settings = QSettings("dieyepy", "dieyepy")
        settings.beginGroup("MainWindow");
        self.resize(settings.value("size", QSize(*initial_main_window_size)))
        self.move(settings.value("pos", QApplication.desktop().screen().rect().center() - self.rect().center()))
        self.slide_viewer_widget.view.setBackgroundBrush(
            settings.value("background_color", QColor(initial_scene_background_color)))
        settings.endGroup()

    def closeEvent(self, event: QCloseEvent) -> None:
        self.write_settings()
        event.accept();

    def add_dynamic_command(self):
        if self.debug:
            input1 = QLineEdit()
            input1.textChanged.connect(self.on_command_text_changed)
            input1.returnPressed.connect(self.on_execute_command_text)
            self.centralWidget().layout().addWidget(input1)
            button1 = QPushButton("Exec")
            button1.clicked.connect(self.on_execute_command_text)
            self.centralWidget().layout().addWidget(button1)

    def on_command_text_changed(self, text):
        self.text = text

    def on_execute_command_text(self):
        # self.slide_viewer_widget.view.set_zoom_in_view_center(0.1)
        print("exec", self.text)
        exec(self.text)
