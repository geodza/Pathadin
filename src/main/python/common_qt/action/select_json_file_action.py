from typing import Optional, List

from PyQt5.QtCore import QObject
from PyQt5.QtWidgets import QFileDialog

from common_qt.action.my_action import MyAction


def show_select_file_dialog(parent: QObject, title: str = 'Select file', save=True, default_file_name="temp",
							mime_types: List[str] = []) -> Optional[str]:
	dialog = QFileDialog(parent)
	dialog.setWindowTitle(title)
	dialog.setMimeTypeFilters(mime_types)
	if mime_types:
		dialog.selectMimeTypeFilter(mime_types[0])
	dialog.selectFile(default_file_name)
	if save:
		dialog.setFileMode(QFileDialog.AnyFile)
		dialog.setAcceptMode(QFileDialog.AcceptSave)
	else:
		dialog.setFileMode(QFileDialog.ExistingFile)
		dialog.setAcceptMode(QFileDialog.AcceptOpen)
	if dialog.exec() and dialog.selectedFiles():
		selected_file = dialog.selectedFiles()[0]
		return selected_file
	else:
		return None


def json_mime_types():
	return [
		"application/json",
	]

def csv_mime_types():
	return [
		"text/csv",
	]

class SelectJsonFileAction(MyAction):
	def __init__(self, title, parent, callback, default_file_name="temp", save=True):
		super().__init__(title, parent, self.on_select_file_path)
		self.title_ = title
		self.callback = callback
		self.default_file_name = default_file_name
		self.save = save

	def on_select_file_path(self):
		file_path = show_select_file_dialog(self.parent(), self.title_, self.save, self.default_file_name,
											json_mime_types())
		if file_path:
			self.callback(file_path)
