import typing
from collections import OrderedDict

from PyQt5.QtCore import QItemSelection, QItemSelectionModel, QModelIndex, QAbstractItemModel, pyqtSignal
from PyQt5.QtWidgets import QTreeView, QWidget, QAbstractItemView

from slide_viewer.ui.dict_tree_view_model.ordered_dicts_tree_model import OrderedDictsTreeModel


class ODictsTreeView(QTreeView):
    modelChanged = pyqtSignal(OrderedDictsTreeModel)
    odictSelected = pyqtSignal(list)
    odictsChanged = pyqtSignal(list)
    odictsRemoved = pyqtSignal(list)
    odictsInserted = pyqtSignal(list)

    def __init__(self, parent: typing.Optional[QWidget] = None) -> None:
        super().__init__(parent)
        # self.setSelectionMode(QAbstractItemView.MultiSelection)
        self.setSelectionMode(QAbstractItemView.ExtendedSelection)
        # self.setSelectionBehavior(QAbstractItemView.SelectItems)
        self.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.setAllColumnsShowFocus(True)
        # self.setItemDelegate()
        # self.setContentsMargins(50, 50, 50, 50)
        # self.resizeColumnToContents()

    def model(self) -> OrderedDictsTreeModel:
        return super().model()

    def rowsInserted(self, parent: QModelIndex, start: int, end: int) -> None:
        super().rowsInserted(parent, start, end)
        self.on_model_rows_inserted(parent, start, end)
        self.span_first_column()

    def rowsAboutToBeRemoved(self, parent: QModelIndex, start: int, end: int) -> None:
        super().rowsAboutToBeRemoved(parent, start, end)
        self.on_model_rows_removed(parent, start, end)

    def dataChanged(self, topLeft: QModelIndex, bottomRight: QModelIndex, roles: typing.Iterable[int] = None) -> None:
        super().dataChanged(topLeft, bottomRight, roles)
        self.on_model_data_changed(topLeft, bottomRight)

    def selectionChanged(self, selected: QItemSelection, deselected: QItemSelection) -> None:
        super().selectionChanged(selected, deselected)
        rows = set(i.row() for i in self.selectionModel().selection().indexes())
        print(f"selected: {rows}")
        #TODO attrs can be selected too
        odict_numbers = self.get_selected_odict_numbers()
        # print(f"OrderedDictsTreeView.selectionChanged: {odict_numbers}")
        self.odictSelected.emit(odict_numbers)

    def setModel(self, model: QAbstractItemModel) -> None:
        super().setModel(model)
        self.span_first_column()
        self.modelChanged.emit(model)

    def span_first_column(self):
        for row in range(self.model().rowCount()):
            self.setFirstColumnSpanned(row, QModelIndex(), True)

    def on_model_data_changed(self, top_left: QModelIndex, bottom_right: QModelIndex):
        # print(f"on_model_data_changed: {top_left}")
        if OrderedDictsTreeModel.is_dict(top_left):
            odict_numbers = [odict_number for odict_number in range(top_left.row(), bottom_right.row() + 1)]
            self.odictsChanged.emit(odict_numbers)
        else:
            odict_numbers = [top_left.parent().row()]
            self.odictsChanged.emit(odict_numbers)

    def on_model_rows_removed(self, parent: QModelIndex, first: int, last: int):
        if OrderedDictsTreeModel.is_dict(parent):
            self.odictsChanged.emit([parent.row()])
        else:
            self.odictsRemoved.emit(list(range(first, last + 1)))

    def on_model_rows_inserted(self, parent: QModelIndex, first: int, last: int):
        if OrderedDictsTreeModel.is_dict(parent):
            self.odictsChanged.emit([parent.row()])
        else:
            self.odictsInserted.emit(list(range(first, last + 1)))

    def get_selected_odict_numbers(self):
        return list(set(index.row() for index in self.selectionModel().selection().indexes()))

    def clear_selection(self):
        self.selectionModel().clear()
