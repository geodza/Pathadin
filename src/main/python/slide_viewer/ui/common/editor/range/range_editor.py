import sys
import typing

from PyQt5 import QtCore, QtGui
from PyQt5.QtCore import Qt, QSize, QMargins, pyqtSignal, QRect, QSignalBlocker
from PyQt5.QtGui import QColor, QPainter, QBrush, QGradient, QLinearGradient, \
    QFont, QFontMetrics
from PyQt5.QtWidgets import QWidget, QHBoxLayout, QApplication, QSlider, QMainWindow, QSplitter, \
    QLabel, QSplitterHandle, QVBoxLayout, QBoxLayout


class RangeEditor(QWidget):
    rangeChanged = pyqtSignal(tuple)

    def __init__(self, min_max: tuple, parent: QWidget = None, range_prefix="",
                 orientation=Qt.Horizontal, invertedAppearance=False, rangeChanged=None) -> None:
        super().__init__(parent)
        self.range_prefix = range_prefix
        self.orientation = orientation
        self.from_slider = QSlider(orientation, self, minimum=min_max[0], maximum=min_max[1], value=min_max[0],
                                   valueChanged=self.onValueChanged, invertedAppearance=invertedAppearance)
        self.to_slider = QSlider(orientation, self, minimum=min_max[0], maximum=min_max[1], value=min_max[1],
                                 valueChanged=self.onValueChanged, invertedAppearance=invertedAppearance)
        if rangeChanged:
            self.rangeChanged.connect(rangeChanged)
        layout = QBoxLayout(QBoxLayout.TopToBottom if orientation == Qt.Horizontal else QBoxLayout.LeftToRight, self)
        layout.addWidget(self.from_slider)
        layout.addWidget(self.to_slider)
        layout.setSpacing(20)
        # layout.setContentsMargins(QMargins())
        self.setLayout(layout)
        self.setBackgroundRole(12)
        # self.setAutoFillBackground(True)

    def get_range(self):
        return (self.from_slider.value(), self.to_slider.value())

    def set_range(self, range_: tuple):
        with QSignalBlocker(self.from_slider):
            self.from_slider.setValue(range_[0])
        with QSignalBlocker(self.to_slider):
            self.to_slider.setValue(range_[1])
        self.onValueChanged(None)

    def onValueChanged(self, not_used_value_of_one_slider):
        range_ = (self.from_slider.value(), self.to_slider.value())
        if range_[0] > range_[1]:
            self.from_slider.setValue(range_[1])  # will result in another onValueChanged
        else:
            self.rangeChanged.emit(range_)
            self.update()

    def paintEvent(self, a0: QtGui.QPaintEvent) -> None:
        # return
        super().paintEvent(a0)
        painter = QPainter(self)
        painter.setPen(Qt.black)
        if self.orientation == Qt.Vertical:
            text_rect = self.rect().transposed()
            painter.translate(self.rect().right(), 0)
            painter.rotate(90)
        else:
            text_rect = self.rect()
        range_ = list(self.get_range())
        r = painter.drawText(text_rect, Qt.AlignCenter, f"{self.range_prefix}{range_}")
        painter.fillRect(r, Qt.white)
        painter.drawText(r, Qt.AlignCenter, f"{self.range_prefix}{range_}")
        # painter.setPen(Qt.red)
        # painter.drawRect(text_rect.adjusted(0, 0, -1, -1))
        painter.end()
