import sys

from PyQt5 import QtCore
from PyQt5.QtCore import QSize
from PyQt5.QtWidgets import QApplication, QMainWindow, QLabel, QWidget, QVBoxLayout

from common_qt.editor.dropdown import Dropdown
from common_qt.util.message_handler import qt_message_handler

QtCore.qInstallMessageHandler(qt_message_handler)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = QMainWindow()

    w = QWidget()
    filter_type_label = QLabel(w)


    def on_filter_type_change(val):
        filter_type_label.setText(f"selected type: {val}")


    filter_type_dropdown = Dropdown(["a","b","c"], w)
    filter_type_dropdown.selectedItemChanged.connect(on_filter_type_change)
    layout = QVBoxLayout(w)
    layout.addWidget(filter_type_dropdown)
    layout.addWidget(filter_type_label)
    w.setLayout(layout)
    window.setCentralWidget(w)

    window.show()
    window.resize(QSize(300, 300))
    sys.exit(app.exec_())
