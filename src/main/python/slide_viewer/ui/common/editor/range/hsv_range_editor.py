import typing

import numpy as np
from PyQt5 import QtGui
from PyQt5.QtCore import Qt, QMargins, pyqtSignal, pyqtProperty, QVariant, QSignalBlocker
from PyQt5.QtGui import QPainter, QPen, QImage
from PyQt5.QtWidgets import QWidget, QLabel, QGridLayout, QSizePolicy

from img.proc.img_mode_convert import convert_pilimage
from img.proc.img_object_convert import expose_ndarray_buffer_to_pillowimage, pilimage_to_qimage
from slide_viewer.ui.common.editor.range.range_editor import RangeEditor


# class Range(typing.NamedTuple):
#     from_: typing.Any
#     to_: typing.Any


# class HSVValue(typing.NamedTuple):
#     h: int
#     s: int
#     v: int
#
#
# class HSVRange(typing.NamedTuple):
#     from_: HSVValue
#     to_: HSVValue


class HSVRangeEditor(QWidget):
    hsvRangeChanged = pyqtSignal(tuple)

    def __init__(self, parent: QWidget = None, hsvRangeChanged=None) -> None:
        super().__init__(parent)
        # TODO is min_max always (0,255)? for any colorspace and any 8,16,24,32-bit images?
        min_max = (0, 255)
        self.h_editor = RangeEditor(min_max, self, "H: ")
        self.s_editor = RangeEditor(min_max, self, "S: ", orientation=Qt.Vertical, invertedAppearance=True)
        self.v_editor = RangeEditor(min_max, self, "V: ", orientation=Qt.Vertical, invertedAppearance=True)
        self.h_editor.rangeChanged.connect(self.onValueChanged)
        self.s_editor.rangeChanged.connect(self.onValueChanged)
        self.v_editor.rangeChanged.connect(self.onValueChanged)
        if hsvRangeChanged:
            self.hsvRangeChanged.connect(hsvRangeChanged)
        self.hue_sat_matrix_label = QLabel()
        self.hue_sat_range_matrix_label = QLabel()
        layout = QGridLayout()
        layout.setContentsMargins(QMargins())
        layout.addWidget(self.hue_sat_matrix_label, 0, 0)
        layout.addWidget(self.h_editor, 1, 0)
        layout.addWidget(self.s_editor, 0, 1)
        layout.addWidget(self.hue_sat_range_matrix_label, 2, 0)
        layout.addWidget(self.v_editor, 2, 1)
        # layout.addWidget(self.v_editor, 2, 0, 1, 2)
        # layout.setSizeConstraint(QLayout.SetNoConstraint)
        self.setLayout(layout)
        # self.setBackgroundRole(12)
        self.setAutoFillBackground(True)
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

        self.hue_sat_matrix_qimg: QImage = None
        self.hue_sat_matrix_arrimg: np.ndarray = None
        self.hue_sat_range_matrix_qimg: QImage = None

        self.init_hue_sat_matrix()
        self.init_hue_sat_range_matrix()
        self.update()

    def init_hue_sat_matrix(self):
        arr = np.full((256, 256, 3), 255, dtype=np.uint8)
        for i, r in enumerate(arr):
            for j, c in enumerate(r):
                c[0] = j
                c[1] = 255 - i
        self.hue_sat_matrix_arrimg = arr
        hue_sat_matrix_img = convert_pilimage(expose_ndarray_buffer_to_pillowimage(arr, "HSV"), "RGB")
        self.hue_sat_matrix_qimg = pilimage_to_qimage(hue_sat_matrix_img)

    def init_hue_sat_range_matrix(self):
        h, s = self.h_editor.get_range(), self.s_editor.get_range()
        sparse_factor = 16
        sparse_matrix_rect = self.hue_sat_matrix_arrimg[s[0]:s[1] + 1:sparse_factor, h[0]:h[1] + 1:sparse_factor, :]
        sparse_matrix_rect_T = np.transpose(sparse_matrix_rect, (1, 0, 2))
        # sparse_matrix_rect_T = sparse_matrix_rect
        sparse_matrix_rect_T_flat = sparse_matrix_rect_T.reshape(-1, 3)
        arr = np.tile(sparse_matrix_rect_T_flat, (255, 1, 1))
        for i, r in enumerate(arr):
            r[:, 2] = i
        # arr = np.transpose(arr, (1, 0, 2)).copy(order='C')
        rgb_img = convert_pilimage(expose_ndarray_buffer_to_pillowimage(arr, "HSV"), "RGB")
        self.hue_sat_range_matrix_qimg = pilimage_to_qimage(rgb_img)

    def get_hsv_range(self):
        h, s, v = self.h_editor.get_range(), self.s_editor.get_range(), self.v_editor.get_range()
        return ((h[0], s[0], v[0]), (h[1], s[1], v[1]))

    def set_hsv_range(self, hsv_range: typing.Tuple[tuple]):
        with QSignalBlocker(self.h_editor):
            self.h_editor.set_range((hsv_range[0][0], hsv_range[1][0]))
        with QSignalBlocker(self.s_editor):
            self.s_editor.set_range((hsv_range[0][1], hsv_range[1][1]))
        with QSignalBlocker(self.v_editor):
            self.v_editor.set_range((hsv_range[0][2], hsv_range[1][2]))
        self.init_hue_sat_range_matrix()
        # self.onValueChanged(None)

    def onValueChanged(self, not_used_value_of_one_range_editor):
        self.init_hue_sat_range_matrix()
        self.update()
        self.hsvRangeChanged.emit(self.get_hsv_range())

    def paintEvent(self, a0: QtGui.QPaintEvent) -> None:
        # super().paintEvent(a0)
        painter = QPainter(self)
        self.paint_hue_sat_matrix(painter)
        self.paint_hue_sat_range_matrix(painter)
        painter.end()

    def paint_hue_sat_matrix(self, painter: QPainter):
        s1 = self.hue_sat_matrix_label.width() / self.hue_sat_matrix_qimg.width()
        s2 = self.hue_sat_matrix_label.height() / self.hue_sat_matrix_qimg.height()
        # print(self.hue_sat_matrix_label.width(), self.hue_sat_matrix_label.height(), s1, s2)
        painter.save()
        painter.translate(self.hue_sat_matrix_label.pos())
        painter.drawImage(self.hue_sat_matrix_label.rect(), self.hue_sat_matrix_qimg)
        painter.scale(s1, s2)
        pen = QPen()
        pen.setCosmetic(True)
        painter.setPen(pen)
        h_range, s_range = self.h_editor.get_range(), self.s_editor.get_range()
        painter.drawRect(h_range[0], s_range[0], h_range[1] - h_range[0], s_range[1] - s_range[0])
        painter.restore()

    def paint_hue_sat_range_matrix(self, painter: QPainter):
        s1 = self.hue_sat_range_matrix_label.width() / self.hue_sat_range_matrix_qimg.width()
        s2 = self.hue_sat_range_matrix_label.height() / self.hue_sat_range_matrix_qimg.height()
        painter.save()
        painter.translate(self.hue_sat_range_matrix_label.pos())
        painter.drawImage(self.hue_sat_range_matrix_label.rect(), self.hue_sat_range_matrix_qimg)
        painter.scale(s1, s2)
        pen = QPen()
        pen.setCosmetic(True)
        painter.setPen(pen)
        v_range = self.v_editor.get_range()
        painter.drawLine(0, v_range[0], self.hue_sat_range_matrix_qimg.width(), v_range[0])
        painter.drawLine(0, v_range[1], self.hue_sat_range_matrix_qimg.width(), v_range[1])
        painter.restore()

    itemProperty = pyqtProperty(QVariant, get_hsv_range, set_hsv_range, user=True)
