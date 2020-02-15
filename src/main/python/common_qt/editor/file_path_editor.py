from typing import List

from PyQt5.QtCore import pyqtProperty, pyqtSignal, QVariant
from PyQt5.QtWidgets import QWidget, QFileDialog


class FilePathEditor(QFileDialog):
    filePathChanged = pyqtSignal(str)

    def __init__(self, parent: QWidget = None, file_path: str = None, title: str = 'Select file', mime_types: List[str] = None) -> None:
        super().__init__(parent)
        self.file_path = file_path
        self.title = title
        self.mime_types = mime_types
        dialog = self
        if self.mime_types:
            dialog.setMimeTypeFilters(self.get_mime_types())
        if self.file_path:
            dialog.selectFile(self.file_path)
        dialog.setWindowTitle(self.title)
        dialog.setFileMode(QFileDialog.ExistingFile)
        dialog.setAcceptMode(QFileDialog.AcceptOpen)
        dialog.fileSelected.connect(self.on_file_selected)

    def get_file_path(self) -> str:
        return self.file_path

    def set_file_path(self, file_path: str):
        self.file_path = file_path

    def on_file_selected(self, file):
        self.file_path = file

    def show_dialog(self) -> None:
        dialog = self
        if not dialog.isVisible():
            dialog.open()

    filePathProperty = pyqtProperty(QVariant, get_file_path, set_file_path, user=True)
