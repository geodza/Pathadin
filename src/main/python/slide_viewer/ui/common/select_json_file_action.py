from PyQt5.QtWidgets import QFileDialog

from slide_viewer.ui.common.my_action import MyAction


class SelectJsonFileAction(MyAction):
    def __init__(self, title, parent, callback, default_file_name="temp", save=True):
        super().__init__(title, parent, self.on_select_file_path)
        self.callback = callback
        self.default_file_name = default_file_name
        self.save = save

    def on_select_file_path(self):
        file_path = self.open_file_name_dialog()
        if file_path:
            self.callback(file_path)

    def get_mime_types(self):
        return [
            "application/json",
        ]

    def open_file_name_dialog(self):
        dialog = QFileDialog(self.parent())
        dialog.setMimeTypeFilters(self.get_mime_types())
        dialog.selectMimeTypeFilter(self.get_mime_types()[0])
        dialog.selectFile(self.default_file_name)
        dialog.setWindowTitle("Select file")
        if self.save:
            dialog.setFileMode(QFileDialog.AnyFile)
            dialog.setAcceptMode(QFileDialog.AcceptSave)
        else:
            dialog.setFileMode(QFileDialog.ExistingFile)
            dialog.setAcceptMode(QFileDialog.AcceptOpen)
        if dialog.exec() and dialog.selectedFiles():
            selected_file = dialog.selectedFiles()[0]
            return selected_file
