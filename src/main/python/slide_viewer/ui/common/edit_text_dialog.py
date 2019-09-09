import typing

from PyQt5 import QtCore
from PyQt5.QtCore import QSize, Qt
from PyQt5.QtGui import QFontMetrics
from PyQt5.QtWidgets import QDialog, QWidget, QVBoxLayout, QTextEdit, QDialogButtonBox

from slide_viewer.ui.common.text_dialog import TextDialog


class EditTextDialog(TextDialog):

    def __init__(self, text: str, parent: typing.Optional[QWidget] = None,
                 flags: typing.Union[QtCore.Qt.WindowFlags, QtCore.Qt.WindowType] = Qt.WindowFlags()) -> None:
        super().__init__(text, text, False, parent, flags)

        button_box = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        self.layout().addWidget(button_box)
        button_box.accepted.connect(self.accept)
        button_box.rejected.connect(self.reject)
