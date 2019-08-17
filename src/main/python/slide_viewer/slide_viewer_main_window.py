from PyQt5.QtGui import QPixmapCache
from PyQt5.QtWidgets import QMainWindow, QWidget, QVBoxLayout, QLineEdit, QPushButton
from PyQt5.QtCore import Qt

from slide_viewer.config import debug
from slide_viewer.my_menu import MyMenu
from slide_viewer.on_load_slide_action import SelectSlideFileAction
from slide_viewer.slide_viewer_widget import SlideViewerWidget


class SlideViewerMainWindow(QMainWindow):

    def __init__(self):
        super().__init__()
        self.text = None
        self.debug = debug

        widget = QWidget(self)
        layout = QVBoxLayout(widget)
        self.slide_viewer_widget = SlideViewerWidget(widget, self.on_load_slide_callback)
        layout.addWidget(self.slide_viewer_widget)
        widget.setLayout(layout)
        self.setCentralWidget(widget)

        menuBar = self.menuBar()
        self.menu = MyMenu("actions", menuBar)
        menuBar.addMenu(self.menu)

        self.select_slide_file_action = SelectSlideFileAction("&load", self, self.on_select_slide_file_action)
        self.menu.addAction(self.select_slide_file_action)

        self.add_dynamic_command()

    def on_select_slide_file_action(self, file_path):
        self.slide_viewer_widget.load(file_path)

    def on_load_slide_callback(self):
        # fitInView must be after show() and resize()
        self.slide_viewer_widget.view.fitInView(self.slide_viewer_widget.scene.sceneRect(),
                                                Qt.KeepAspectRatio)

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
        print("exec", self.text)
        exec(self.text)
