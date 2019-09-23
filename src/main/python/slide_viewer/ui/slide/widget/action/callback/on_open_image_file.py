from PyQt5.QtWidgets import QFileDialog

from slide_viewer.ui.common.formats import whole_slide_formats, pillow_formats
from slide_viewer.ui.slide.widget.slide_viewer_widget import SlideViewerWidget


def on_open_image_file(w: SlideViewerWidget):
    available_formats = [*whole_slide_formats, *pillow_formats]
    available_extensions = ["." + available_format for available_format in available_formats]
    file_ext_strings = ["*" + ext for ext in available_extensions]
    file_ext_string = " ".join(file_ext_strings)
    file_name, _ = QFileDialog.getOpenFileName(w, "Select image to view", "",
                                               "Image formats ({});;".format(file_ext_string))
    if file_name:
        w.load(file_name)
