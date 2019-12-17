import sys

from PyQt5 import QtCore
from PyQt5.QtCore import QSize
from PyQt5.QtWidgets import QApplication, QMainWindow, QLabel, QWidget, QVBoxLayout

from slide_viewer.ui.common.editor.dropdown import Dropdown
from slide_viewer.common_qt.message_handler import qt_message_handler
from img.filter.base_filter import FilterType

QtCore.qInstallMessageHandler(qt_message_handler)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = QMainWindow()

    w = QWidget()
    filter_type_label = QLabel(w)


    def on_filter_type_change(val):
        filter_type_label.setText(f"selected type: {val}")


    filter_type_dropdown = Dropdown(list(FilterType), w)
    filter_type_dropdown.selectedItemChanged.connect(on_filter_type_change)
    layout = QVBoxLayout(w)
    layout.addWidget(filter_type_dropdown)
    layout.addWidget(filter_type_label)
    w.setLayout(layout)
    window.setCentralWidget(w)

    window.show()
    window.resize(QSize(300, 300))
    sys.exit(app.exec_())
