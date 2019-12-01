import typing
from collections import OrderedDict

from PyQt5.QtCore import QItemSelection, QModelIndex, pyqtSignal
from PyQt5.QtWidgets import QTreeView, QWidget, QAbstractItemView, QHeaderView
from dataclasses import dataclass, InitVar

from slide_viewer.ui.odict.deep.deepable_tree_model import DeepableTreeModel


@dataclass
class DeepableTreeView(QTreeView):
    parent_: InitVar[typing.Optional[QWidget]] = None
    model_: InitVar[DeepableTreeModel] = DeepableTreeModel(_root=OrderedDict())

    objectsSelected = pyqtSignal(list)

    def __post_init__(self, parent_: typing.Optional[QWidget], model_: DeepableTreeModel):
        super().__init__(parent_)
        self.setSelectionMode(QAbstractItemView.ExtendedSelection)
        self.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.setAllColumnsShowFocus(True)
        self.header().setSectionResizeMode(QHeaderView.ResizeToContents)
        self.header().hide()
        self.setModel(model_)
        # self.delegate = ODictsTreeViewDelegate()
        # self.setItemDelegate(self.delegate)

    def model(self) -> DeepableTreeModel:
        return typing.cast(DeepableTreeModel, super().model())

    def rowsInserted(self, parent: QModelIndex, start: int, end: int) -> None:
        super().rowsInserted(parent, start, end)
        self.span_first_column()

    def selectionChanged(self, selected: QItemSelection, deselected: QItemSelection) -> None:
        super().selectionChanged(selected, deselected)
        # keys = self.model().indexes_to_keys(selected.indexes())
        keys = self.model().indexes_to_keys(self.selectionModel().selection().indexes())
        self.objectsSelected.emit(keys)

    def setModel(self, model: DeepableTreeModel) -> None:
        super().setModel(model)
        self.span_first_column()

    def span_first_column(self):
        for row in range(self.model().rowCount()):
            self.setFirstColumnSpanned(row, QModelIndex(), True)
