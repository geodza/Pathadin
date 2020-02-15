import sys
import typing

from PyQt5 import QtCore, QtGui
from PyQt5.QtCore import Qt, QSize, QMargins, pyqtSignal
from PyQt5.QtGui import QColor, QPainter, QBrush, QGradient, QLinearGradient, \
    QFont, QFontMetrics
from PyQt5.QtWidgets import QWidget, QHBoxLayout, QApplication, QSlider, QMainWindow, QSplitter, \
    QLabel, QSplitterHandle, QVBoxLayout


class SliderSplitterHandle(QSplitterHandle):

    def __init__(self, o: QtCore.Qt.Orientation, parent: QSplitter) -> None:
        super().__init__(o, parent)

    def paintEvent(self, a0: QtGui.QPaintEvent) -> None:
        painter = QPainter(self)
        painter.fillRect(a0.rect(), QBrush(QColor("red")))


class SliderRangeSplitter(QSplitter):

    def __init__(self, orientation: Qt.Orientation, parent: QWidget):
        super().__init__(orientation, parent)
        self.gradient = QLinearGradient(0, 0, 1, 0)
        self.gradient.setCoordinateMode(QGradient.StretchToDeviceMode)
        self.gradient_brush = QBrush(self.gradient)

    def paintEvent(self, a0: QtGui.QPaintEvent) -> None:
        painter = QPainter(self)
        painter.fillRect(a0.rect(), self.gradient_brush)

    def createHandle(self) -> QSplitterHandle:
        return SliderSplitterHandle(self.orientation(), self)


class SliderRangeEditorSplitter(QWidget):
    rangeChange = pyqtSignal(tuple)

    def __init__(self, parent: QWidget = None,
                 flags: typing.Union[QtCore.Qt.WindowFlags, QtCore.Qt.WindowType] = Qt.WindowFlags()) -> None:
        super().__init__(parent, flags)
        layout = QHBoxLayout(self)
        self.splitter = SliderRangeSplitter(Qt.Horizontal, self)
        self.splitter.splitterMoved.connect(self.on_splitter_moved)
        for i in range(3):
            self.splitter.addWidget(QLabel())
        self.splitter.setHandleWidth(0)
        layout.addWidget(QLabel("0"))
        layout.addWidget(self.splitter)
        layout.addWidget(QLabel("255"))
        layout.setContentsMargins(QMargins())
        self.setLayout(layout)
        h = QFontMetrics(QFont()).height()
        self.setFixedHeight(h * 1.5)

    def on_splitter_moved(self, pos: int, index: int):
        # logical_pos = self.splitter_value_to_logical_value(pos)
        # print(f"pos: {pos}, index: {index}, logical_range: {self.get_total_logical_range()} logical_pos: {logical_pos}")
        # print(f"logical_ranges: {self.get_logical_ranges()}")
        print(f"main_range: {self.get_main_range()}")
        # print(self.splitter.getRange(1), self.splitter.getRange(2))
        # print(self.splitter.sizes())
        self.rangeChange.emit(self.get_main_range())

    def get_total_logical_range(self):
        hw = self.splitter.handleWidth()
        return self.splitter.width() - hw

    def get_logical_ranges(self):
        sizes = self.splitter.sizes()
        positions = [0]
        for i, size in enumerate(sizes):
            positions.append(positions[i] + size)
        logical_positions = [self.splitter_value_to_logical_value(pos) for pos in positions]
        logical_ranges = [(logical_positions[i], pos) for i, pos in enumerate(logical_positions[1:])]
        return logical_ranges

    def update_by_main_logical_range(self, range_: tuple):
        logical_positions = [0, range_[0], range_[1], 1]
        splitter_positions = [self.logical_value_to_splitter_value(pos) for pos in logical_positions]
        sizes = [pos - splitter_positions[i] for i, pos in enumerate(splitter_positions[1:])]
        self.splitter.setSizes(sizes)

    def get_main_range(self):
        return self.get_logical_ranges()[1]

    def splitter_value_to_logical_value(self, value: int):
        return value / self.splitter.width()

    def logical_value_to_splitter_value(self, value: int):
        return value * self.splitter.width()


class SliderRangeEditor(QWidget):

    def __init__(self, orientation: Qt.Orientation, parent: QWidget = None) -> None:
        super().__init__(parent)
        self.from_slider = QSlider(orientation, self)
        self.to_slider = QSlider(orientation, self)
        self.to_slider.setValue(50)

    def paintEvent(self, ev: QtGui.QPaintEvent) -> None:
        super().paintEvent(ev)
        self.from_slider.paintEvent(ev)
        self.to_slider.paintEvent(ev)

