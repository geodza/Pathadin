from PyQt5.QtWidgets import QFileDialog

from slide_viewer.ui.common.action.my_action import MyAction
from slide_viewer.common_qt.img_formats import saveable_mime_types


class SelectImageFileAction(MyAction):
    def __init__(self, title, parent, callback, default_file_name="temp"):
        super().__init__(title, parent, self.on_select_image_file)
        self.callback = callback
        self.default_file_name = default_file_name

    def on_select_image_file(self):
        file_path = self.open_file_name_dialog()
        if file_path:
            self.callback(file_path)

    def get_mime_types(self):
        return saveable_mime_types

    def open_file_name_dialog(self):
        dialog = QFileDialog(self.parent())
        dialog.setFileMode(QFileDialog.AnyFile)
        dialog.setMimeTypeFilters(self.get_mime_types())
        dialog.selectMimeTypeFilter(self.get_mime_types()[0])
        dialog.selectFile(self.default_file_name)
        dialog.setWindowTitle("Select file")
        dialog.setAcceptMode(QFileDialog.AcceptSave)
        if dialog.exec() and dialog.selectedFiles():
            selected_file = dialog.selectedFiles()[0]
            return selected_file
