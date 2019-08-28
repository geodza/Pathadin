from PyQt5.QtCore import QMimeDatabase
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

    def get_mime_types(self):
        return [
            "image/jpeg",
            "image/tiff",
            "image/bmp",
            "image/png",
            "image/x-portable-bitmap",
            "image/x-portable-graymap",
            "image/x-portable-pixmap",
            "image/x-xbitmap",
            "image/x-xpixmap"
        ]

    def open_file_name_dialog(self):
        dialog = QFileDialog(self.parent())
        dialog.setFileMode(QFileDialog.AnyFile)
        dialog.setMimeTypeFilters(self.get_mime_types())
        dialog.setWindowTitle("Select file")
        dialog.setAcceptMode(QFileDialog.AcceptSave)
        if dialog.exec() and dialog.selectedFiles():
            selected_file = dialog.selectedFiles()[0]
            return selected_file
