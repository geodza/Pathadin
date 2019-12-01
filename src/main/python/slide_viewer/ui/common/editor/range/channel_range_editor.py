import sys

import cv2
import numpy as np
from PIL import Image
from PyQt5 import QtGui
from PyQt5.QtCore import Qt, QSize, QMargins, pyqtSignal
from PyQt5.QtGui import QPainter, QBrush, QGradient, QLinearGradient
from PyQt5.QtWidgets import QWidget, QApplication, QMainWindow, QLabel, QVBoxLayout

from slide_viewer.ui.common.img.img_mode_convert import convert_pilimage
from slide_viewer.ui.common.img.img_object_convert import expose_pilimage_buffer_to_ndarray, \
    expose_ndarray_buffer_to_pillowimage, pilimage_to_qimage


# def build_gradient(mode: str, channel_number: int):
#     stops=[]
#     if mode == "RGB":
#         g = QLinearGradient(0, 0, 1, 0)
#         if channel_number == 0:
#             stops.append((0,QColor().fromRgb(0,0,0))


class ChannelRangeEditor(QWidget):
    rangeChanged = pyqtSignal(tuple)

    def __init__(self, from_to: tuple, color_pattern: Image.Image, channel_number: int, parent: QWidget = None) -> None:
        super().__init__(parent)
        # TODO is min_max always (0,255)? for any colorspace and any 8,16,24,32-bit images?
        min_max = (0, 255)
        # self.range_editor = RangeEditor(from_to, min_max, self)
        self.range_editor.rangeChanged.connect(self.onValueChanged)
        self.channel_number = channel_number
        self.set_color_pattern(color_pattern)
        layout = QVBoxLayout(self)
        layout.addWidget(self.range_editor)

        layout.setContentsMargins(QMargins())
        self.setLayout(layout)

    def set_color_pattern(self, color_pattern: Image.Image):
        channel_number = self.channel_number
        color_pattern_arr = expose_pilimage_buffer_to_ndarray(color_pattern)
        color_range = range(0, 255, 5)
        n_stops = len(color_range)
        arr = np.full((255, 255, 3), 255, dtype=np.uint8)
        for i, r in enumerate(arr):
            for j, c in enumerate(r):
                c[0] = j
                c[1] = 255 - i
        rgb_img = convert_pilimage(expose_ndarray_buffer_to_pillowimage(arr, "HSV"), "RGB")
        self.matrix_img = pilimage_to_qimage(rgb_img)

    def set_color_pattern3(self, color_pattern: Image.Image):
        channel_number = self.channel_number
        color_pattern_arr = expose_pilimage_buffer_to_ndarray(color_pattern)
        color_range = range(0, 255, 5)
        n_stops = len(color_range)
        self.gradient = QLinearGradient(0, 0, 1, 0)
        for stop, color in enumerate(color_range):
            color_to = np.array(color_pattern_arr)
            color_to[:, :, channel_number] = color
            color_to_rgba = convert_pilimage(expose_ndarray_buffer_to_pillowimage(color_to, color_pattern.mode), "RGB")
            rgba_to = pilimage_to_qimage(color_to_rgba).pixelColor(0, 0)
            self.gradient.setColorAt(stop / n_stops, rgba_to)
            # self.gradient.setColorAt(stop / n_stops, QColor().fromHsv(color, 255, 255))
        # self.gradient.setColorAt(1, QColor().fromHsv(360, 255, 255))
        # self.gradient = QLinearGradient(0, 0, 1, 0)
        # self.gradient.setColorAt(0,QColor().fromHsv(0,255,255))
        # self.gradient.setColorAt(1,QColor().fromHsv(300,255,255))
        self.gradient.setCoordinateMode(QGradient.StretchToDeviceMode)
        self.gradient_brush = QBrush(self.gradient)

    def set_color_pattern2(self, color_pattern: Image.Image):
        channel_number = self.channel_number
        color_pattern_arr = expose_pilimage_buffer_to_ndarray(color_pattern)
        color_from = np.array(color_pattern_arr)
        color_from[:, :, channel_number] = 0
        color_to = np.array(color_pattern_arr)
        color_to[:, :, channel_number] = 255
        color_from_rgba = convert_pilimage(expose_ndarray_buffer_to_pillowimage(color_from, color_pattern.mode), "RGB")
        color_to_rgba = convert_pilimage(expose_ndarray_buffer_to_pillowimage(color_to, color_pattern.mode), "RGB")
        rgba_from = pilimage_to_qimage(color_from_rgba).pixelColor(0, 0)
        rgba_to = pilimage_to_qimage(color_to_rgba).pixelColor(0, 0)
        self.gradient = QLinearGradient(0, 0, 1, 0)
        self.gradient.setColorAt(0, rgba_from)
        self.gradient.setColorAt(1, rgba_to)
        self.gradient.setCoordinateMode(QGradient.StretchToDeviceMode)
        self.gradient_brush = QBrush(self.gradient)

    def onValueChanged(self, value):
        self.update()
        self.rangeChanged.emit(value)

    def paintEvent(self, a0: QtGui.QPaintEvent) -> None:
        painter = QPainter(self)
        # painter.fillRect(self.rect(), self.gradient_brush)
        painter.drawImage(self.rect(), self.matrix_img)
        painter.end()
        # super().paintEvent(a0)
        # a0.ignore()
        painter = QPainter(self)
        painter.setPen(Qt.black)
        # painter.fillRect(self.rect(), self.gradient_brush)
        range_ = [self.range_editor.from_slider.value(), self.range_editor.to_slider.value()]
        r = painter.drawText(self.rect(), Qt.AlignCenter, f"{range_}")
        painter.fillRect(r, Qt.white)
        painter.drawText(self.rect(), Qt.AlignCenter, f"{range_}")
        painter.end()
        a0.accept()


sys.excepthook = sys.excepthook

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = QMainWindow()


    def update_label_by_range(range_):
        label.setText(f"range: [{range_[0]}, {range_[1]}]")


    green = np.uint8([[[255, 0, 0]]])
    hsv_green = cv2.cvtColor(green, cv2.COLOR_RGB2HSV)
    print(hsv_green)
    green_rgb = cv2.cvtColor(hsv_green, cv2.COLOR_HSV2RGB)
    print(green_rgb)

    print(";")
    print(cv2.cvtColor(np.uint8([[[0, 255, 255]]]), cv2.COLOR_HSV2RGB))
    print(cv2.cvtColor(np.uint8([[[120, 255, 255]]]), cv2.COLOR_HSV2RGB))
    print(cv2.cvtColor(np.uint8([[[255, 255, 255]]]), cv2.COLOR_HSV2RGB))

    selected_color = (0, 0, 255)
    color_pattern = Image.new("LAB", (1, 1), selected_color)
    # color_pattern = Image.new("RGB", (1, 1), selected_color)
    # rr = (QColor(0, 0, 0), QColor(255, 0, 0))
    # gr = (QColor(0, 0, 0), QColor(0, 255, 0))
    # br = (QColor(0, 0, 0), QColor(0, 0, 255))
    crr = ChannelRangeEditor((10, 100), color_pattern, 0, window)
    cgr = ChannelRangeEditor((10, 100), color_pattern, 1, window)
    cbr = ChannelRangeEditor((10, 100), color_pattern, 2, window)
    # sre.rangeChanged.connect(update_label_by_range)
    # crr.rangeChanged.connect()

    label = QLabel()

    w = QWidget()
    layout = QVBoxLayout(w)
    layout.addWidget(crr)
    layout.addWidget(cgr)
    layout.addWidget(cbr)
    layout.addWidget(label)
    w.setLayout(layout)
    window.setCentralWidget(w)

    window.show()
    window.resize(QSize(300, 300))
    sys.exit(app.exec_())
