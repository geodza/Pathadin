import typing

from PyQt5.QtCore import QItemSelection, QItemSelectionModel, QModelIndex, QAbstractItemModel, pyqtSignal
from PyQt5.QtWidgets import QTreeView, QWidget, QAbstractItemView

from slide_viewer.ui.dict_tree_view_model.ordered_dicts_tree_model import OrderedDictsTreeModel


class OrderedDictsTreeView(QTreeView):
    odictSelected = pyqtSignal(int)
    odictsChanged = pyqtSignal(list)
    odictsRemoved = pyqtSignal(list)
    odictsInserted = pyqtSignal(list)

    def __init__(self, parent: typing.Optional[QWidget] = None) -> None:
        super().__init__(parent)
        self.setSelectionBehavior(QAbstractItemView.SelectItems)
        self.setSelectionMode(QAbstractItemView.SingleSelection)
        self.setAllColumnsShowFocus(True)

    def model(self) -> OrderedDictsTreeModel:
        return super().model()

    def selectionChanged(self, selected: QItemSelection, deselected: QItemSelection) -> None:
        # we allow to select both odicts and attrs, but if attr_key is selected we want its parent also to be selected
        dict_rows = [index.parent().row() for index in self.selectionModel().selectedIndexes() if
                     OrderedDictsTreeModel.is_attr(index)]
        for dict_row in dict_rows:
            dict_selection = QItemSelection(self.model().index(dict_row, 0), self.model().index(dict_row, 1))
            self.selectionModel().select(dict_selection, QItemSelectionModel.Select | QItemSelectionModel.Rows)
        super().selectionChanged(self.selectionModel().selection(), deselected)

    def rowsInserted(self, parent: QModelIndex, start: int, end: int) -> None:
        super().rowsInserted(parent, start, end)
        self.span_first_column()

    def setModel(self, model: QAbstractItemModel) -> None:
        super().setModel(model)
        self.span_first_column()
        self.model().dataChanged.connect(self.on_model_data_changed)
        self.model().rowsInserted.connect(self.on_model_rows_inserted)
        self.model().rowsRemoved.connect(self.on_model_rows_removed)
        self.selectionModel().currentChanged.connect(self.on_current_changed)

    def span_first_column(self):
        for row in range(self.model().rowCount()):
            self.setFirstColumnSpanned(row, QModelIndex(), True)

    def on_current_changed(self, current: QModelIndex, previous: QModelIndex):
        if OrderedDictsTreeModel.is_dict(current):
            self.odictSelected.emit(current.row())
        elif OrderedDictsTreeModel.is_attr(current):
            self.odictSelected.emit(current.parent().row())

    def on_model_data_changed(self, top_left: QModelIndex, bottom_right: QModelIndex):
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

    def select_odict(self, odict_number: int):
        odict_index = self.model().index(odict_number, 0)
        self.selectionModel().select(odict_index, QItemSelectionModel.ClearAndSelect | QItemSelectionModel.Rows)
        self.odictSelected.emit(odict_number)

    def clear_selection(self):
        self.selectionModel().clear()
