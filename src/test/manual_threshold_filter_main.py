import sys

import dataclasses
from PyQt5 import QtCore
from PyQt5.QtCore import QSize
from PyQt5.QtWidgets import QWidget, QHBoxLayout, QApplication, QMainWindow, QLabel, QVBoxLayout, QPushButton, \
    QFileDialog

from slide_viewer.common.debounce import debounce
from slide_viewer.ui.common.editor.dropdown import Dropdown
from slide_viewer.ui.common.editor.range.gray_range_editor import GrayRangeEditor
from slide_viewer.ui.common.editor.range.hsv_range_editor import HSVRangeEditor
from slide_viewer.common_qt.img_formats import whole_slide_formats, pillow_formats
from slide_viewer.common_qt.message_handler import qt_message_handler
from slide_viewer.filter.filter_processing import build_source_, \
    mask_result_
from img.proc.region import RegionData
from img.filter.threshold_filter import ThresholdType
from img.filter.manual_threshold import ManualThresholdFilterData
from img.filter.base_filter import FilterType
from src.test.config import img_path

QtCore.qInstallMessageHandler(qt_message_handler)


def main():
    app = QApplication(sys.argv)
    window = QMainWindow()
    label = QLabel()
    source_img_label = QLabel()
    result_img_label = QLabel()
    # source_img_label.setMaximumWidth(300)
    source_img_label.setMaximumSize(500, 500)
    # def wh(self, w):
    #     return w * source_img_label.pixmap().height() / source_img_label.pixmap().width()
    #
    # source_img_label.heightForWidth = wh.__get__(source_img_label, source_img_label.__class__)
    source_img_label.setScaledContents(True)
    result_img_label.setMaximumSize(500, 500)
    result_img_label.setScaledContents(True)

    points1 = ((0, 0), (500, 0), (250, 500), (0, 0))
    region_data = RegionData(img_path, 0, (0, 0), None)
    filter_data = ManualThresholdFilterData("1", FilterType.THRESHOLD, ThresholdType.MANUAL, 'HSV',
                                            ((0, 0, 0), (255, 255, 255)))
    filter_region_data = FilterRegionData(region_data, None, None, filter_data, None, None)

    @debounce(0.3)
    def update_images():
        source_img = build_source_(region_data)
        source_img_label.setPixmap(source_img.toqpixmap())
        result_img = mask_result_(region_data, None, filter_data)
        result_img_label.setPixmap(result_img.toqpixmap())

    def on_file():
        available_formats = [*whole_slide_formats, *pillow_formats]
        available_extensions = ["." + available_format for available_format in available_formats]
        file_ext_strings = ["*" + ext for ext in available_extensions]
        file_ext_string = " ".join(file_ext_strings)
        file_name, _ = QFileDialog.getOpenFileName(w, "Select image to view", "",
                                                   "Image formats ({});;".format(file_ext_string))
        if file_name:
            nonlocal region_data
            region_data = region_data._replace(img_path=file_name)
            update_images()

    def on_hsv_range_change(hsv_range):
        if hsv_range:
            nonlocal filter_data
            filter_data = dataclasses.replace(filter_data, threshold_range=hsv_range, color_mode='HSV')
            update_images()

    def on_gray_range_change(gray_range):
        if gray_range:
            nonlocal filter_data
            filter_data = dataclasses.replace(filter_data, threshold_range=gray_range, color_mode='L')
            update_images()

    w = QWidget()
    layout = QVBoxLayout(w)

    def on_color_mode_change(color_mode):
        nonlocal filter_data
        old_li = layout.takeAt(3)
        if old_li:
            old_w = old_li.widget()
            old_w.deleteLater()
            del old_li
        if color_mode == 'L':
            filter_data = dataclasses.replace(filter_data, threshold_range=((0,), (255,)))
            layout.insertWidget(3,
                                GrayRangeEditor(filter_data.threshold_range, w, grayRangeChanged=on_gray_range_change))
        elif color_mode == 'HSV':
            filter_data = dataclasses.replace(filter_data, threshold_range=((0, 0, 0), (255, 255, 255)))
            hsv_range_editor = HSVRangeEditor(w, hsvRangeChanged=on_hsv_range_change)
            hsv_range_editor.set_hsv_range(filter_data.threshold_range)
            layout.insertWidget(3, hsv_range_editor)
        layout.invalidate()

    b = QPushButton("file", w, clicked=on_file)
    layout.addWidget(b)
    color_mode_dropdown = Dropdown(['HSV', 'L'], filter_data.color_mode, w, on_color_mode_change)
    layout.addWidget(color_mode_dropdown)

    img_layout = QHBoxLayout(w)
    img_layout.addWidget(source_img_label)
    img_layout.addWidget(result_img_label)
    layout.addLayout(img_layout)
    w.setLayout(layout)
    window.setCentralWidget(w)

    window.show()
    window.resize(QSize(300, 700))
    update_images()
    on_color_mode_change(filter_data.color_mode)
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
