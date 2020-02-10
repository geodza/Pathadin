from PyQt5.QtWidgets import QFileDialog

from slide_viewer.common.img_formats import whole_slide_formats, pillow_formats
from slide_viewer.ui.slide.graphics.view.graphics_view import GraphicsView


def on_open_image_file(view: GraphicsView) -> None:
    available_formats = [*whole_slide_formats, *pillow_formats]
    available_extensions = ["." + available_format for available_format in available_formats]
    file_ext_strings = ["*" + ext for ext in available_extensions]
    file_ext_string = " ".join(file_ext_strings)
    file_name, _ = QFileDialog.getOpenFileName(view, "Select image to view", "",
                                               "Image formats ({});;".format(file_ext_string))
    if file_name:
        view.set_file_path(file_name)
