from typing import List, Any, Optional

from PyQt5.QtCore import QObject, Qt, QModelIndex, pyqtProperty, QSize, QMargins, QStringListModel
from PyQt5.QtGui import QColor, QStandardItemModel, QIcon
from PyQt5.QtWidgets import QWidget, QComboBox, QHBoxLayout, QItemEditorCreatorBase, QPushButton, QColorDialog, \
    QStyledItemDelegate, QStyleOptionViewItem, QItemEditorFactory, QApplication, QListWidget, QListView, \
    QAbstractScrollArea


class SelectListModel(QStringListModel):

    def __init__(self, selected_values, all_values, parent: Optional[QObject] = None) -> None:
        super().__init__(all_values, parent)
        self.selected_values = list(selected_values)
        self.all_values = list(all_values)

    def flags(self, index: QModelIndex) -> Qt.ItemFlags:
        return Qt.ItemIsEnabled | Qt.ItemIsUserCheckable

    def data(self, index: QModelIndex, role: int) -> Any:
        if role == Qt.CheckStateRole:
            return index.data(Qt.DisplayRole) in self.selected_values
        else:
            return super().data(index, role)

    def setData(self, index: QModelIndex, value: Any, role: int = Qt.EditRole) -> bool:
        if role == Qt.CheckStateRole:
            value = index.data(Qt.DisplayRole)
            if value in self.selected_values:
                self.selected_values.remove(value)
            else:
                self.selected_values.append(value)
            self.dataChanged.emit(index, index)
            return True
        else:
            return super().setData(index, value, role)


class SelectListEditor(QListView):

    def __init__(self, values: list, parent: QWidget = None) -> None:
        super().__init__(parent)
        self.values = values
        # self.setSizeAdjustPolicy(QAbstractScrollArea.AdjustToContents)
        # editor.setResizeMode(QListView.Adjust)
        # editor.setsize(QAbstractScrollArea.AdjustToContents)

        # editor.setMinimumHeight(200)

    def get_selected_values(self) -> List[str]:
        return list(self.model().selected_values)

    def set_selected_values(self, selected_values: list):
        self.setModel(SelectListModel(selected_values, self.values))

    selectedValuesProperty = pyqtProperty(list, get_selected_values, set_selected_values, user=True)
