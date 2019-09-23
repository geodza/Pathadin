import typing

from PyQt5 import QtCore
from PyQt5.QtCore import QObject, Qt, QModelIndex, pyqtProperty, QSize, QMargins
from PyQt5.QtGui import QColor, QStandardItemModel
from PyQt5.QtWidgets import QWidget, QComboBox, QHBoxLayout, QItemEditorCreatorBase, QPushButton, QColorDialog, \
    QStyledItemDelegate, QStyleOptionViewItem, QItemEditorFactory


class CustomItemEditorFactory(QItemEditorFactory):

    def __init__(self, system_item_editor_factory: QItemEditorFactory, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.custom_editor_factories = {}
        self.system_item_editor_factory = system_item_editor_factory

    def createEditor(self, userType: int, parent: QWidget) -> QWidget:
        if userType in self.custom_editor_factories:
            factory = self.custom_editor_factories[userType]
            return factory.createEditor(userType, parent)
        else:
            return self.system_item_editor_factory.createEditor(userType, parent)

    def registerEditor(self, userType: int, creator: QItemEditorCreatorBase) -> None:
        factory = QItemEditorFactory()
        factory.registerEditor(userType, creator)
        self.custom_editor_factories[userType] = factory


class ColorDelegate(QStyledItemDelegate):

    def __init__(self, parent: QObject = None) -> None:
        super().__init__(parent)

    def createEditor(self, parent: QWidget, option: QStyleOptionViewItem, index: QtCore.QModelIndex) -> QWidget:
        return super().createEditor(parent, option, index)


class ColorEditor(QWidget):

    def __init__(self, button_icon, parent: QWidget = None,
                 flags: typing.Union[QtCore.Qt.WindowFlags, QtCore.Qt.WindowType] = Qt.WindowFlags()) -> None:
        super().__init__(parent, flags)
        self.combobox = QComboBox(self)
        self.combobox.setEditable(False)
        # self.combobox.setDuplicatesEnabled(False)
        # self.combobox.setInsertPolicy(QComboBox.InsertAtTop)
        # self.combobox.currentIndexChanged.connect(self.on_index_changed)
        for i, color_name in enumerate(QColor.colorNames()):
            color = QColor(color_name)
            self.combobox.insertItem(i, color_name)
            self.combobox.setItemData(i, color, Qt.DecorationRole)
        self.setLayout(QHBoxLayout(self))
        self.layout().addWidget(self.combobox)
        # button = QPushButton(button_icon, None, self)
        # self.layout().addWidget(button)
        self.layout().setContentsMargins(QMargins())

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

    # def on_index_changed(self, *args):
    #     print(*args)

    def get_color(self) -> QColor:
        return QColor(self.combobox.currentData(Qt.DisplayRole))

    def set_color(self, color: QColor):
        index = self.combobox.findData(color, Qt.DecorationRole)
        self.combobox.setCurrentIndex(index)

    colorProperty = pyqtProperty(QColor, get_color, set_color, user=True)


class ColorEditorCreatorBase(QItemEditorCreatorBase):

    def __init__(self, button_icon, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.button_icon = button_icon

    def createWidget(self, parent: QWidget) -> QWidget:
        return ColorEditor(self.button_icon, parent)
