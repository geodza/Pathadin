from PyQt5.QtCore import Qt, pyqtProperty, QMargins
from PyQt5.QtGui import QColor
from PyQt5.QtWidgets import QWidget, QComboBox, QHBoxLayout, QItemEditorCreatorBase

from slide_viewer.common_qt.persistent_settings.user_custom_color import get_user_custom_color_names, \
    add_user_custom_color


# class ColorDelegate(QStyledItemDelegate):
#
#     def __init__(self, parent: QObject = None) -> None:
#         super().__init__(parent)
#
#     def createEditor(self, parent: QWidget, option: QStyleOptionViewItem, index: QtCore.QModelIndex) -> QWidget:
#         return super().createEditor(parent, option, index)


class ColorEditorCreatorBase(QItemEditorCreatorBase):

    def __init__(self, button_icon, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.button_icon = button_icon

    def createWidget(self, parent: QWidget) -> QWidget:
        return ColorEditor(self.button_icon, parent)


class ColorEditor(QWidget):

    def __init__(self, button_icon, parent: QWidget = None) -> None:
        super().__init__(parent)
        self.combobox_color_names = list(reversed(get_user_custom_color_names()))
        self.combobox_color_names.extend(QColor.colorNames())
        self.combobox = QComboBox(self)
        self.combobox.setEditable(True)
        self.combobox.setDuplicatesEnabled(False)
        self.combobox.setInsertPolicy(QComboBox.InsertAtTop)
        for i, color_name in enumerate(self.combobox_color_names):
            color = QColor(color_name)
            self.combobox.insertItem(i, color_name)
            self.combobox.setItemData(i, color, Qt.DecorationRole)
        layout = QHBoxLayout(self)
        layout.addWidget(self.combobox)
        # button = QPushButton(button_icon or QIcon(), None, self)
        # layout.addWidget(button)
        # layout.addStretch()
        layout.setContentsMargins(QMargins())
        self.setLayout(layout)

        white_color = QColor()
        if not white_color:
            print(f"empty: {white_color.name()}")

    # def on_select_color_dialog(self):
    #     def on_color_change(color):
    #         self.set_color(color)
    #
    #     color_dialog = QColorDialog(Qt.white, self)
    #     color_dialog.setOptions(QColorDialog.ShowAlphaChannel)
    #     last_color = self.get_color()
    #     color_dialog.currentColorChanged.connect(on_background_color_change)
    #     color_dialog.colorSelected.connect(on_background_color_change)
    #     res = color_dialog.exec()
    #     if not res:
    #         view.setBackgroundBrush(last_color)

    def get_color(self) -> str:
        color_name = self.combobox.currentData(Qt.DisplayRole)
        if color_name not in self.combobox_color_names:
            custom_color = QColor(color_name)
            add_user_custom_color(custom_color)
        return color_name

    def set_color(self, color_name: str):
        index = self.combobox.findData(color_name, Qt.DisplayRole)
        self.combobox.setCurrentIndex(index)

    colorProperty = pyqtProperty(str, get_color, set_color, user=True)
