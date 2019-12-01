from PyQt5 import QtGui
from PyQt5.QtCore import Qt, QMargins, pyqtSignal, pyqtProperty, QVariant
from PyQt5.QtGui import QPainter, QPen, QLinearGradient, QGradient, QBrush
from PyQt5.QtWidgets import QWidget, QLabel, QGridLayout

from slide_viewer.common_qt.slot_disconnected import slot_disconnected
from slide_viewer.ui.common.editor.range.range_editor import RangeEditor


class GrayRangeEditor(QWidget):
    grayRangeChanged = pyqtSignal(tuple)

    def __init__(self, parent: QWidget = None, grayRangeChanged=None) -> None:
        super().__init__(parent)
        min_max = (0, 255)
        self.gray_editor = RangeEditor(min_max, self, range_prefix="Gray: ")
        self.gray_editor.rangeChanged.connect(self.onValueChanged)
        if grayRangeChanged:
            self.grayRangeChanged.connect(grayRangeChanged)
        self.img_label = QLabel()
        layout = QGridLayout(self)
        layout.setContentsMargins(QMargins())
        layout.addWidget(self.img_label, 0, 0)
        layout.addWidget(self.gray_editor, 1, 0)
        self.setLayout(layout)
        self.setAutoFillBackground(True)

        self.gradient = QLinearGradient(0, 0, 1, 0)
        self.gradient.setColorAt(0, Qt.black)
        self.gradient.setColorAt(1, Qt.white)
        self.gradient.setCoordinateMode(QGradient.StretchToDeviceMode)
        self.gradient_brush = QBrush(self.gradient)

    def get_range(self):
        return self.gray_editor.get_range()

    def set_range(self, range_: tuple):
        with slot_disconnected(self.gray_editor.rangeChanged, self.onValueChanged):
            self.gray_editor.set_range(range_)

    def onValueChanged(self, value):
        self.update()
        self.grayRangeChanged.emit(self.get_range())

    def paintEvent(self, a0: QtGui.QPaintEvent) -> None:
        painter = QPainter(self)
        s1 = self.img_label.width() / 255
        s2 = self.img_label.height() / 255
        painter.save()
        painter.translate(self.img_label.pos())
        painter.setBrush(self.gradient_brush)
        painter.drawRect(self.img_label.rect())
        painter.scale(s1, s2)
        pen = QPen(Qt.red)
        pen.setCosmetic(True)
        painter.setPen(pen)
        range_ = self.gray_editor.get_range()
        painter.drawLine(range_[0], 0, range_[0], 255)
        painter.drawLine(range_[1], 0, range_[1], 255)
        painter.restore()
        painter.end()
        super().paintEvent(a0)

    itemProperty = pyqtProperty(QVariant, get_range, set_range, user=True)
