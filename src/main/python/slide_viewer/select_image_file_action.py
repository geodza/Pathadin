from PyQt5.QtWidgets import QFileDialog

from slide_viewer.my_action import MyAction


class SelectImageFileAction(MyAction):
    def __init__(self, title, parent, callback):
        super().__init__(title, parent, self.on_select_image_file)
        self.callback = callback

    def on_select_image_file(self):
        file_path = self.open_file_name_dialog()
        if file_path:
            self.callback(file_path)

    def get_available_image_formats(self):
        available_qt_formats = [
            "BMP",
            "GIF",
            "JPG",
            "PNG",
            "PBM",
            "PGM",
            "PPM",
            "XBM",
            "XPM",
            "SVG",
        ]
        available_extensions = ["." + available_format for available_format in available_qt_formats]
        return available_extensions

    def open_file_name_dialog(self):
        options = QFileDialog.Options()
        file_ext_strings = ["*" + ext for ext in self.get_available_image_formats()]
        file_ext_string = " ".join(file_ext_strings)
        file_name, _ = QFileDialog.getSaveFileName(self.window, "Select file", "screenshot.png",
                                                   "supported formats ({});;".format(file_ext_string),
                                                   options=options)
        return file_name
