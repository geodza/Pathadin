import typing

from PyQt5 import QtCore
from PyQt5.QtCore import QSize, Qt
from PyQt5.QtGui import QFontMetrics
from PyQt5.QtWidgets import QDialog, QWidget, QVBoxLayout, QTextEdit


class TextDialog(QDialog):

    def __init__(self, text: str, text_for_height: str, readonly=True, parent: typing.Optional[QWidget] = None,
                 flags: typing.Union[QtCore.Qt.WindowFlags, QtCore.Qt.WindowType] = Qt.WindowFlags()) -> None:
        super().__init__(parent, flags)
        layout = QVBoxLayout(self)
        self.setLayout(layout)
        self.text_editor = QTextEdit(self)
        self.text_editor.setReadOnly(readonly)
        layout.addWidget(self.text_editor)

        self.text_editor.setText(text)

        font = self.text_editor.document().defaultFont()
        font_metrics = QFontMetrics(font)
        text_width = font_metrics.size(0, text).width()
        main_text_height = font_metrics.size(0, text_for_height).height() / 2

        margins = self.layout().contentsMargins()
        margins_size = QSize(margins.left() + margins.right(), margins.top() + margins.bottom())
        margins_size += QSize(self.text_editor.horizontalScrollBar().height(), self.text_editor.verticalScrollBar().width())
        if parent and text_width > parent.width():
            text_width = parent.width()
        if parent and main_text_height > parent.height():
            main_text_height = parent.width()
        size = QSize(text_width, main_text_height) + margins_size
        self.resize(size)
