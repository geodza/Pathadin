import json
from collections import OrderedDict
from datetime import datetime

from PyQt5.QtCore import Qt, QSize, QSettings, QFileInfo, QFile, QPoint
from PyQt5.QtGui import QCloseEvent, QGuiApplication
from PyQt5.QtGui import QColor
from PyQt5.QtWidgets import QMainWindow, QWidget, QVBoxLayout, QLineEdit, QPushButton, QAction, QDialog, \
    QSpinBox, QHBoxLayout, QFormLayout, QDialogButtonBox, QColorDialog, QApplication, QToolTip, QActionGroup

import json_utils
from slide_viewer.config import debug, initial_main_window_size, initial_scene_background_color
from slide_viewer.ui.annotation.annotation_type import AnnotationType
from slide_viewer.ui.annotation.annotation_utls import ordered_dict_to_data
from slide_viewer.ui.common.my_action import MyAction
from slide_viewer.ui.common.my_menu import MyMenu
from slide_viewer.ui.common.select_image_file_action import SelectImageFileAction
from slide_viewer.ui.common.select_json_file_action import SelectJsonFileAction
from slide_viewer.ui.common.text_dialog import TextDialog
from slide_viewer.ui.dict_tree_view_model.ordered_dicts_tree_model import OrderedDictsTreeModel
from slide_viewer.ui.slide.on_load_slide_action import SelectSlideFileAction
from slide_viewer.ui.slide.screenshot_builders import build_screenshot_image_from_view
from slide_viewer.ui.slide.slide_viewer_widget import SlideViewerWidget


class SlideViewerMainWindow(QMainWindow):

    def __init__(self, ctx):
        super().__init__()
        self.ctx = ctx
        self.text = None
        self.debug = debug
        self.dynamic_zoom_actions = []
        self.props_dialog = None

        widget = QWidget(self)
        layout = QVBoxLayout(widget)
        self.slide_viewer_widget = SlideViewerWidget(widget, self.on_load_slide_callback)
        self.slide_viewer_widget.view.scaleChanged.connect(self.on_view_zoom_changed)
        self.slide_viewer_widget.slideFileChanged.connect(self.on_slide_file_changed)
        layout.addWidget(self.slide_viewer_widget)
        widget.setLayout(layout)
        self.setCentralWidget(widget)

        self.main_toolbar = self.addToolBar("main_toolbar")
        self.main_toolbar.layout().setSpacing(5)
        self.main_toolbar.setIconSize(QSize(24, 24))

        menuBar = self.menuBar()
        self.actions_menu = MyMenu("Actions", menuBar)
        menuBar.addMenu(self.actions_menu)
        # zoom_menu is dynamically populated in on_select_slide_file_action
        self.zoom_menu = MyMenu("Zoom", menuBar)
        menuBar.addMenu(self.zoom_menu)
        self.grid_menu = MyMenu("Grid", menuBar)
        menuBar.addMenu(self.grid_menu)
        self.annotations_menu = MyMenu("Annotations", menuBar)
        menuBar.addMenu(self.annotations_menu)

        self.export_annotations_action = MyAction("&Export annotations as JSON", self.annotations_menu,
                                                  self.on_export_annotations)
        self.import_annotations_action = MyAction("&Import annotations as JSON", self.annotations_menu,
                                                  self.on_import_annotations)

        self.select_slide_file_action = SelectSlideFileAction("&Open image", self.actions_menu,
                                                              self.on_select_slide_file_action, self.ctx.icon_open)
        self.main_toolbar.addAction(self.select_slide_file_action)

        self.show_properties_action = MyAction("Show &properties", self.actions_menu,
                                               self.on_show_properties_action, self.ctx.icon_description)
        self.main_toolbar.addAction(self.show_properties_action)

        self.grid_toggle_action = MyAction("Toggle &grid", self.grid_menu, self.on_grid_toggle, self.ctx.icon_grid)
        self.main_toolbar.addAction(self.grid_toggle_action)

        self.grid_change_size_action = MyAction("Grid &size", self.grid_menu, self.on_grid_change_size_action)

        self.take_screenshot_action = MyAction("&Save screenshot", self.actions_menu, self.on_take_screenshot_action,
                                               self.ctx.icon_screenshot)
        self.main_toolbar.addAction(self.take_screenshot_action)

        self.copy_screenshot_action = MyAction("&Copy screenshot to clipboard", self.actions_menu,
                                               self.on_copy_screenshot_action,
                                               self.ctx.icon_camera)
        self.main_toolbar.addAction(self.copy_screenshot_action)

        self.select_background_color_action = MyAction("&Background color", self.actions_menu,
                                                       self.on_select_background_color_action, self.ctx.icon_palette)
        self.add_dynamic_command()

        self.annotation_group = QActionGroup(self.actions_menu)
        separator = QAction(self.annotation_group)
        separator.setSeparator(True)
        self.pan_tool = MyAction("&Pan/select tool", self.annotation_group,
                                 None, self.ctx.icon_pan_tool, None)
        self.pan_tool.setCheckable(True)
        self.pan_tool.setChecked(True)
        self.line_annotation = MyAction("&Line annotation", self.annotation_group,
                                        None, self.ctx.icon_line, AnnotationType.LINE)
        self.line_annotation.setCheckable(True)
        self.rect_annotation = MyAction("&Rect annotation", self.annotation_group,
                                        None, self.ctx.icon_rect, AnnotationType.RECT)
        self.rect_annotation.setCheckable(True)
        self.ellipse_annotation = MyAction("&Ellipse annotation", self.annotation_group,
                                           None, self.ctx.icon_ellipse, AnnotationType.ELLIPSE)
        self.ellipse_annotation.setCheckable(True)
        self.polygon_annotation = MyAction("&Polygon annotation. Press Enter to close current polygon",
                                           self.annotation_group,
                                           None, self.ctx.icon_polygon, AnnotationType.POLYGON)
        self.polygon_annotation.setCheckable(True)
        separator = QAction(self.annotation_group)
        separator.setSeparator(True)
        self.annotation_group.triggered.connect(self.on_annotation_group)
        self.main_toolbar.addActions(self.annotation_group.actions())

        self.fit_action = MyAction("&Fit", self.zoom_menu, None, self.ctx.icon_fit, "fit")
        self.main_toolbar.addAction(self.fit_action)

        self.zoom_action = MyAction("zoom", self, self.on_zoom_line_edit_pressed, self.ctx.icon_magnifier)
        self.main_toolbar.addAction(self.zoom_action)
        self.zoom_menu.triggered.connect(self.on_zoom_menu_action)

        self.zoom_line_edit = QLineEdit()
        self.zoom_line_edit.returnPressed.connect(self.on_zoom_line_edit_pressed)
        self.zoom_line_edit.setMaximumWidth(50)
        self.main_toolbar.addWidget(self.zoom_line_edit)

        self.read_settings()

    def on_annotation_group(self, action: QAction):
        if action == self.pan_tool:
            self.slide_viewer_widget.view.annotation_type = None
            if self.slide_viewer_widget.view.annotation_item:
                self.slide_viewer_widget.scene.removeItem(self.slide_viewer_widget.view.annotation_item)
                self.slide_viewer_widget.view.annotation_item = None
                self.slide_viewer_widget.view.annotation_item_in_progress = False
            return
        annotation_type = action.data()
        self.slide_viewer_widget.view.annotation_type = annotation_type
        self.slide_viewer_widget.view.annotation_item_in_progress = False
        # action.setChecked(True)

    def on_view_zoom_changed(self, scale):
        # self.zoom_line_edit.setText("{:.4F}".format(new_scale))
        zoom = self.slide_viewer_widget.slide_helper.scale_to_zoom(scale)
        self.zoom_line_edit.setText("{:.1f}".format(zoom))

    def on_slide_file_changed(self, new_slide_file):
        self.update_dynamic_zoom_actions(new_slide_file)

    def on_select_slide_file_action(self, file_path):
        self.slide_viewer_widget.load(file_path)

    def update_dynamic_zoom_actions(self, file_path):
        for action in self.dynamic_zoom_actions:
            self.zoom_menu.removeAction(action)
            self.main_toolbar.removeAction(action)
        self.dynamic_zoom_actions = []
        slide_helper = self.slide_viewer_widget.slide_helper
        for downsample in slide_helper.level_downsamples:
            zoom = int(slide_helper.downsample_to_zoom(downsample))
            if zoom > 0:
                action_text = "x{}".format(zoom)
                scale = self.slide_viewer_widget.slide_helper.zoom_to_scale(zoom)
                scale_action = MyAction(action_text, self.zoom_menu, None, None, scale)
                f = scale_action.font()
                f.setPointSize(11)
                scale_action.setFont(f)
                self.dynamic_zoom_actions.append(scale_action)
                self.zoom_menu.addAction(scale_action)
                self.main_toolbar.addAction(scale_action)

    def on_zoom_menu_action(self, action: QAction):
        if not self.slide_viewer_widget.slide_helper:
            return
        if action != self.fit_action:
            scale = action.data()
            self.slide_viewer_widget.view.set_scale_in_view_center(scale)
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
            scale = self.slide_viewer_widget.slide_helper.zoom_to_scale(zoom)
            self.slide_viewer_widget.view.set_scale_in_view_center(scale)
        except:
            pass

    def on_copy_screenshot_action(self):
        if self.slide_viewer_widget.slide_graphics_grid_item:
            image = build_screenshot_image_from_view(self.slide_viewer_widget.view)
            QGuiApplication.clipboard().setImage(image)
            for w in self.sender().associatedWidgets():
                if w.parent() == self.main_toolbar:
                    pos = w.mapToGlobal(QPoint()) + QPoint(w.width(), w.height())
                    QToolTip.showText(pos, "Screenshot copied to clipboard!")

    def on_take_screenshot_action(self):
        def on_select_image_file(image_file: str):
            image = build_screenshot_image_from_view(self.slide_viewer_widget.view)
            image.save(image_file)

        if self.slide_viewer_widget.slide_graphics_grid_item:
            now = datetime.now()
            now_str = now.strftime("%d-%m-%Y_%H-%M-%S")
            slide_name = QFileInfo(QFile(self.slide_viewer_widget.slide_helper.slide_path)).baseName()
            default_file_name = f"{slide_name}_screen_{now_str}"
            select_image_file_action = SelectImageFileAction("internal", self, on_select_image_file, default_file_name)
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

    def on_show_properties_action(self):
        if not self.slide_viewer_widget.slide_helper:
            return
        props = self.slide_viewer_widget.slide_helper.get_properties()
        main_props = {prop: val for prop, val in props.items() if prop.startswith("openslide")}
        ordered_props = OrderedDict(main_props.items())
        ordered_props.update(props)
        main_props_text = json.dumps(main_props, indent=2)
        full_props_text = json.dumps(ordered_props, indent=2)

        if self.props_dialog:
            self.props_dialog.close()
        self.props_dialog = TextDialog(full_props_text, main_props_text, True, self)
        self.props_dialog.show()

    def on_export_annotations(self):
        def on_select_file(file_path: str):
            odicts = self.slide_viewer_widget.odicts_widget.view.model().odicts
            json_utils.write(file_path, odicts)

        if self.slide_viewer_widget.slide_helper:
            slide_name = QFileInfo(QFile(self.slide_viewer_widget.slide_helper.slide_path)).baseName()
            default_file_name = f"{slide_name}_annotations"
            select_image_file_action = SelectJsonFileAction("internal", self, on_select_file, default_file_name)
            select_image_file_action.trigger()

    def on_import_annotations(self):
        def on_select_file(file_path: str):
            odicts = json_utils.read(file_path)
            self.slide_viewer_widget.view.on_off_annotation_item()
            self.slide_viewer_widget.odicts_widget.view.setModel(OrderedDictsTreeModel(odicts))
            annotation_data = [ordered_dict_to_data(odict) for odict in odicts]
            self.slide_viewer_widget.view.reset_annotation_items(annotation_data)

        if self.slide_viewer_widget.slide_helper:
            slide_name = QFileInfo(QFile(self.slide_viewer_widget.slide_helper.slide_path)).baseName()
            default_file_name = f"{slide_name}_annotations"
            select_image_file_action = SelectJsonFileAction("internal", self, on_select_file, default_file_name, False)
            select_image_file_action.trigger()

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
        # self.slide_viewer_widget.view.set_scale_in_view_center(0.1)
        print("exec", self.text)
        exec(self.text)
