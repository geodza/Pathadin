import sys

from PyQt5 import QtCore
from PyQt5.QtCore import QSize
from PyQt5.QtWidgets import QWidget, QHBoxLayout, QApplication, QMainWindow, QLabel, QVBoxLayout, QPushButton, QFileDialog

from slide_viewer.ui.common.img.img_formats import whole_slide_formats, pillow_formats
from slide_viewer.common_qt.message_handler import qt_message_handler
from slide_viewer.filter.filter_processing import build_source_, \
    mask_source_
from slide_viewer.ui.model.filter.region_data import RegionData
from src.test.config import img_path

QtCore.qInstallMessageHandler(qt_message_handler)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = QMainWindow()
    label = QLabel()
    source_img_label = QLabel()
    result_img_label = QLabel()
    source_img_label.setMaximumHeight(300)
    source_img_label.setScaledContents(True)
    result_img_label.setMaximumHeight(300)
    result_img_label.setScaledContents(True)

    region_data = RegionData(img_path, 0, (0, 0),
                             ((0, 0), (500, 0), (250, 500), (0, 0)))


    def on_file():
        available_formats = [*whole_slide_formats, *pillow_formats]
        available_extensions = ["." + available_format for available_format in available_formats]
        file_ext_strings = ["*" + ext for ext in available_extensions]
        file_ext_string = " ".join(file_ext_strings)
        file_name, _ = QFileDialog.getOpenFileName(w, "Select image to view", "",
                                                   "Image formats ({});;".format(file_ext_string))
        if file_name:
            new_region_data = region_data._replace(img_path=file_name)

            source_img = build_source_(new_region_data)
            source_img_label.setPixmap(source_img.toqpixmap())
            masked_source_img = mask_source_(new_region_data)
            result_img_label.setPixmap(masked_source_img.toqpixmap())


    w = QWidget()
    layout = QVBoxLayout(w)
    b = QPushButton("file", w)
    b.clicked.connect(on_file)
    layout.addWidget(b)
    img_layout = QHBoxLayout(w)
    img_layout.addWidget(source_img_label)
    img_layout.addWidget(result_img_label)
    layout.addLayout(img_layout)
    w.setLayout(layout)
    window.setCentralWidget(w)

    window.show()
    window.resize(QSize(300, 700))
    sys.exit(app.exec_())
