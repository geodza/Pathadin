import copy

from PyQt5.QtCore import QSize, QSettings, QFileInfo, QFile, QVariant
from PyQt5.QtGui import QCloseEvent
from PyQt5.QtGui import QColor
from PyQt5.QtWidgets import QMainWindow, QWidget, QVBoxLayout, QLineEdit, QPushButton, QApplication, QItemEditorFactory, \
    QStyledItemDelegate

import json_utils
from slide_viewer.config import debug, initial_main_window_size, initial_scene_background_color
from slide_viewer.ui.common.color_editor import ColorEditorCreatorBase, CustomItemEditorFactory
from slide_viewer.ui.common.select_json_file_action import SelectJsonFileAction
from slide_viewer.ui.dict_tree_view_model.ordered_dicts_tree_model import OrderedDictsTreeModel
from slide_viewer.ui.slide.widget.slide_viewer_widget import SlideViewerWidget


class SlideViewerMainWindow(QMainWindow):

    def __init__(self, ctx):
        super().__init__()
        self.ctx = ctx
        self.dynamic_command_line_edit = None

        central_widget = QWidget(self)
        layout = QVBoxLayout(central_widget)
        self.slide_viewer_widget = SlideViewerWidget(central_widget)
        layout.addWidget(self.slide_viewer_widget)
        central_widget.setLayout(layout)
        self.setCentralWidget(central_widget)
        self.read_settings()

        # self.setup_editor_factory()

    def setup_editor_factory(self):
        self.system_default_factory = QItemEditorFactory.defaultFactory()
        # editor_factory = QItemEditorFactory()
        editor_factory = CustomItemEditorFactory(self.system_default_factory)
        # editor_factory = QItemEditorFactory.defaultFactory()
        editor_factory.registerEditor(QVariant.Color, ColorEditorCreatorBase(self.ctx.icon_palette))
        QItemEditorFactory.setDefaultFactory(editor_factory)

    def write_settings(self):
        settings = QSettings("dieyepy", "dieyepy")
        settings.beginGroup("MainWindow")
        settings.setValue("size", self.size())
        settings.setValue("pos", self.pos())
        settings.setValue("background_color", self.slide_viewer_widget.view.backgroundBrush().color())
        settings.endGroup()

    def read_settings(self):
        settings = QSettings("dieyepy", "dieyepy")
        settings.beginGroup("MainWindow")
        self.resize(settings.value("size", QSize(*initial_main_window_size)))
        self.move(settings.value("pos", QApplication.desktop().screen().rect().center() - self.rect().center()))
        self.slide_viewer_widget.view.setBackgroundBrush(
            settings.value("background_color", QColor(initial_scene_background_color)))
        settings.endGroup()

    def closeEvent(self, event: QCloseEvent) -> None:
        self.write_settings()
        # QItemEditorFactory.setDefaultFactory(self.system_default_factory)
        event.accept()

    def add_dynamic_command(self):
        if debug:
            self.dynamic_command_line_edit = QLineEdit()
            self.dynamic_command_line_edit.returnPressed.connect(self.on_execute_command_text)
            self.centralWidget().layout().addWidget(self.dynamic_command_line_edit)
            button1 = QPushButton("Exec")
            button1.clicked.connect(self.on_execute_command_text)
            self.centralWidget().layout().addWidget(button1)

    def on_execute_command_text(self):
        dynamic_command_text = self.dynamic_command_text.text()
        print("exec", dynamic_command_text)
        exec(dynamic_command_text)
