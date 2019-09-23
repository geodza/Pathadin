import typing
from collections import OrderedDict

from PyQt5.QtCore import QItemSelection, QItemSelectionModel, QModelIndex, QAbstractItemModel, pyqtSignal
from PyQt5.QtWidgets import QTreeView, QWidget, QAbstractItemView

from slide_viewer.ui.dict_tree_view_model.ordered_dicts_tree_model import OrderedDictsTreeModel
from slide_viewer.ui.dict_tree_view_model.standard_attr_key import StandardAttrKey, ui_attr_keys


class OrderedDictsTreeView(QTreeView):
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
        odict_numbers = self.get_selected_odict_numbers()
        # print(f"OrderedDictsTreeView.selectionChanged: {odict_numbers}")
        self.odictSelected.emit(odict_numbers)

    def currentChanged(self, current: QModelIndex, previous: QModelIndex) -> None:
        super().currentChanged(current, previous)
        # self.on_current_changed(current, previous)

    def setModel(self, model: QAbstractItemModel) -> None:
        super().setModel(model)
        self.span_first_column()
        # self.model().dataChanged.connect(self.on_model_data_changed)
        # self.model().rowsInserted.connect(self.on_model_rows_inserted)
        # self.model().rowsRemoved.connect(self.on_model_rows_removed)
        # self.selectionModel().currentChanged.connect(self.on_current_changed)
        self.update_hidden([self.model().index(row, 0) for row in range(self.model().rowCount())])
        self.modelChanged.emit(model)

    def span_first_column(self):
        for row in range(self.model().rowCount()):
            self.setFirstColumnSpanned(row, QModelIndex(), True)

    def on_model_data_changed(self, top_left: QModelIndex, bottom_right: QModelIndex):
        if OrderedDictsTreeModel.is_dict(top_left):
            self.update_hidden([self.model().index(row, 0) for row in range(top_left.row(), bottom_right.row())])
            odict_numbers = [odict_number for odict_number in range(top_left.row(), bottom_right.row() + 1)]
            self.odictsChanged.emit(odict_numbers)
        else:
            self.update_hidden([top_left.parent()])
            odict_numbers = [top_left.parent().row()]
            self.odictsChanged.emit(odict_numbers)

    def update_hidden(self, odict_indices: list):
        for odict_index in odict_indices:
            odict = self.model().get_odict(odict_index.row())
            hidden = odict.get(StandardAttrKey.ui_attrs_hidden.name, False)
            for i, attr_key in enumerate(odict.keys()):
                if attr_key in ui_attr_keys:
                    self.setRowHidden(i, odict_index, hidden)

    def on_model_rows_removed(self, parent: QModelIndex, first: int, last: int):
        if OrderedDictsTreeModel.is_dict(parent):
            self.odictsChanged.emit([parent.row()])
        else:
            self.odictsRemoved.emit(list(range(first, last + 1)))

    def on_model_rows_inserted(self, parent: QModelIndex, first: int, last: int):
        if OrderedDictsTreeModel.is_dict(parent):
            self.update_hidden([parent])
            self.odictsChanged.emit([parent.row()])
        else:
            self.update_hidden([self.model().index(row, 0) for row in range(first, last + 1)])
            self.odictsInserted.emit(list(range(first, last + 1)))

    def select_odicts(self, odict_numbers: list):
        if set(self.get_selected_odict_numbers()) == set(odict_numbers):
            return
        selection = QItemSelection()
        for odict_number in odict_numbers:
            odict_index = self.model().index(odict_number, 0)
            selection.select(odict_index, odict_index)
            self.selectionModel().select(selection, QItemSelectionModel.ClearAndSelect | QItemSelectionModel.Rows)

    def get_selected_odict_numbers(self):
        return list(set(index.row() for index in self.selectionModel().selection().indexes()))

    def clear_selection(self):
        self.selectionModel().clear()
