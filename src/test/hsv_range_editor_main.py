import sys

import cv2
import numpy as np
from PyQt5 import QtCore
from PyQt5.QtCore import QSize
from PyQt5.QtWidgets import QApplication, QMainWindow, QLabel, QWidget, QVBoxLayout
from skimage import io

from common_image.core.mode_convert import convert_ndarray
from common_qt.util.message_handler import qt_message_handler
from common_qt.editor.range.hsv_range_editor import HSVRangeEditor

QtCore.qInstallMessageHandler(qt_message_handler)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = QMainWindow()

    label = QLabel()


    def update_label_by_range(range_):
        t = f"h: [{range_[0][0]},{range_[1][0]}], s: [{range_[0][1]},{range_[1][1]}], v: [{range_[0][2]},{range_[1][2]}]"
        label.setText(t)


    green = np.uint8([[[255, 0, 0]]])
    hsv_green = cv2.cvtColor(green, cv2.COLOR_RGB2HSV)
    print(hsv_green)
    green_rgb = cv2.cvtColor(hsv_green, cv2.COLOR_HSV2RGB)
    print(green_rgb)

    print(";")
    print(cv2.cvtColor(np.uint8([[[0, 255, 255]]]), cv2.COLOR_HSV2RGB))
    print(cv2.cvtColor(np.uint8([[[120, 255, 255]]]), cv2.COLOR_HSV2RGB))
    print(cv2.cvtColor(np.uint8([[[255, 255, 255]]]), cv2.COLOR_HSV2RGB))

    range_editor = HSVRangeEditor(window)
    ndimg = convert_ndarray(range_editor.hue_sat_matrix_arrimg, 'HSV', 'RGB')
    io.imsave(r"D:\\temp\\slides_more\\hsv_hue_sat.png", ndimg)
    range_editor.set_hsv_range(((0, 10, 10), (0, 100, 100)))
    range_editor.hsvRangeChanged.connect(update_label_by_range)

    w = QWidget()
    layout = QVBoxLayout(w)
    layout.addWidget(range_editor)
    layout.addWidget(label)
    w.setLayout(layout)
    window.setCentralWidget(w)

    window.show()
    window.resize(QSize(300, 300))
    sys.exit(app.exec_())
