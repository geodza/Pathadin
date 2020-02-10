import sys

from PyQt5.QtCore import QSize
from PyQt5.QtWidgets import QApplication, QMainWindow, QLabel, QWidget, QVBoxLayout

from slide_viewer.ui.common.editor.range import SliderRangeEditorSplitter

sys.excepthook = sys.excepthook

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = QMainWindow()
    # sre = SliderRangeEditor(Qt.Horizontal, window)
    sre = SliderRangeEditorSplitter(window)


    def update_label_by_range(range_):
        label.setText(f"range: [{range_[0]}, {range_[1]}]")


    label = QLabel()
    range_ = (10, 900)
    sre.update_by_main_logical_range(range_)
    update_label_by_range(range_)

    vs = sre.update_by_main_logical_range(range_)
    r2 = sre.get_main_range()


    def on_range_change(range_: tuple):
        update_label_by_range(range_)


    sre.rangeChange.connect(on_range_change)
    w = QWidget()
    layout = QVBoxLayout(w)
    layout.addWidget(sre)
    layout.addWidget(label)
    w.setLayout(layout)
    window.setCentralWidget(w)

    window.show()
    window.resize(QSize(700, 700))
    sys.exit(app.exec_())
