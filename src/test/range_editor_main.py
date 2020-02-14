import sys

from PyQt5.QtCore import QSize, Qt
from PyQt5.QtWidgets import QApplication, QMainWindow, QLabel, QWidget, QVBoxLayout

from slide_viewer.ui.common.editor.range.range_editor import RangeEditor

sys.excepthook = sys.excepthook

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = QMainWindow()


    def update_label_by_range(range_):
        label.setText(f"range: [{range_[0]}, {range_[1]}]")


    sre = RangeEditor((0, 255), window, orientation=Qt.Horizontal)
    sre.set_range((0, 100))
    sre.rangeChanged.connect(update_label_by_range)

    label = QLabel()

    w = QWidget()
    layout = QVBoxLayout(w)
    layout.addWidget(sre)
    layout.addWidget(label)
    w.setLayout(layout)
    window.setCentralWidget(w)

    window.show()
    window.resize(QSize(300, 300))
    sys.exit(app.exec_())
