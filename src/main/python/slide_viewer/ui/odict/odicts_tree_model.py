import typing
from collections import OrderedDict
from enum import Enum

from PyQt5.QtCore import Qt, QAbstractItemModel, QObject, QModelIndex, QSize
from PyQt5.QtGui import QColor, QBrush

from slide_viewer.ui.common.common import join_odict_values
from slide_viewer.ui.odict.odict import ODict2, ODictAttr


class ODictsTreeModelSelectMode(Enum):
    none = 1
    odict_rows = 2
    attr_rows = 3


class ODictsTreeModel(QAbstractItemModel):

    def __init__(self, odicts: typing.List[ODict2] = [], read_only_attrs=[], select_mode=ODictsTreeModelSelectMode.none,
                 radio_attr=None,
                 parent: typing.Optional[QObject] = None) -> None:
        super().__init__(parent)
        self.odicts = odicts if odicts else []
        self.read_only_attrs = read_only_attrs if read_only_attrs else []
        self.read_only_attrs.extend([attr.name for attr in ODictAttr])
        self.select_mode = select_mode
        self.radio_attr = radio_attr
        self.column_headers = ["Key", "Value"]

        self.pyqt_bug_weak_ref_dict = dict()
        self.odict_new_attr_counter = {}

    def columnCount(self, parent: QModelIndex = QModelIndex()) -> int:
        return 2

    def rowCount(self, parent: QModelIndex = QModelIndex()) -> int:
        if self.is_attr(parent):
            return 0
        elif self.is_dict(parent):
            odict = self.odicts[parent.row()]
            return len(odict)
        else:
            return len(self.odicts)

    def index(self, row: int, column: int, parent: QModelIndex = QModelIndex()) -> QModelIndex:
        if parent.isValid():
            self.pyqt_bug_weak_ref_dict.setdefault(parent.row(), [parent.row()])
            parent_row = self.pyqt_bug_weak_ref_dict[parent.row()]
            # we have to store position of parent to be able to restore
            # it in parent() method (qt model-view requirement)
            return self.createIndex(row, column, parent_row)
        else:
            return self.createIndex(row, column, None)

    def parent(self, index: QModelIndex) -> QModelIndex:
        parent_row = index.internalPointer()
        if parent_row is not None:
            return self.createIndex(parent_row[0], 0, None)
        return QModelIndex()

    def headerData(self, section: int, orientation: Qt.Orientation, role: int = Qt.DisplayRole) -> typing.Any:
        if role == Qt.DisplayRole:
            return self.column_headers[section]
        else:
            return super().headerData(section, orientation, role)

    def data(self, index: QModelIndex, role: int = Qt.DisplayRole) -> typing.Any:
        if not self.hasIndex(index.row(), index.column(), index.parent()):
            print("not self.hasIndex(index.row(), index.column(), index.parent())")
            return
        if self.is_attr(index):
            return self.data_attr(index, role)
        elif self.is_dict(index):
            return self.data_odict(index, role)
        # return

    def setData(self, index: QModelIndex, value: typing.Any, role: int = Qt.EditRole) -> bool:
        # print(f"setData {index} {value}")
        if self.is_attr_value(index) and role == Qt.EditRole:
            self.edit_attr(index.parent().row(), index.row(), value)
            return True
        elif self.is_dict(index) and role == Qt.CheckStateRole:
            odict = self.get_odict(index.row())
            attr_key = odict.get(ODictAttr.odict_checked_attr.name)
            if attr_key:
                self.edit_attr_by_key(index.row(), attr_key, value == 1)
                return True

        return super().setData(index, value, role)

    @staticmethod
    def is_attr(index: QModelIndex):
        return index.isValid() and index.parent().isValid()

    @staticmethod
    def is_attr_key(index: QModelIndex):
        return ODictsTreeModel.is_attr(index) and index.column() == 0

    @staticmethod
    def is_attr_value(index: QModelIndex):
        return ODictsTreeModel.is_attr(index) and index.column() == 1

    @staticmethod
    def is_dict(index: QModelIndex):
        return index.isValid() and not index.parent().isValid()

    def flags(self, index: QModelIndex) -> Qt.ItemFlags:
        # only attr values are editable because keys have order position inside OrderedDict
        flags = super().flags(index)
        if self.is_attr(index):
            if self.is_attr_hidden(index):
                flags &= ~(Qt.ItemIsSelectable | Qt.ItemIsEditable)
            else:
                if self.select_mode == ODictsTreeModelSelectMode.attr_rows:
                    flags |= Qt.ItemIsSelectable
                else:
                    flags &= ~Qt.ItemIsSelectable
                if self.is_attr_value(index) and index.sibling(index.row(), 0) not in self.read_only_attrs:
                    flags |= Qt.ItemIsEditable
                else:
                    flags &= ~Qt.ItemIsEditable
        elif self.is_dict(index):
            if self.select_mode == ODictsTreeModelSelectMode.odict_rows:
                flags |= Qt.ItemIsSelectable
            else:
                flags &= ~Qt.ItemIsSelectable
            if self.radio_attr:
                flags |= Qt.ItemIsUserTristate | Qt.ItemIsUserCheckable

        return flags

    def data_attr(self, index: QModelIndex, role: int = Qt.DisplayRole):
        if role == Qt.DisplayRole or role == Qt.EditRole:
            odict_tuple = self.get_attr_tuple(index.parent().row(), index.row())
            odict_tuple_value = odict_tuple[index.column()]
            return odict_tuple_value
        elif role == Qt.SizeHintRole and self.is_attr_hidden(index):
            return QSize()

    def is_attr_hidden(self, index: QModelIndex):
        odict: OrderedDict = self.get_odict(index.parent().row())
        odict_tuple = list(odict.items())[index.row()]
        odict_tuple_key = odict_tuple[0]
        return odict_tuple_key in odict.get(ODictAttr.odict_hidden_attrs.name, [])

    def data_odict(self, index: QModelIndex, role: int = Qt.DisplayRole):
        if index.column() != 0:
            return
        odict: OrderedDict = self.get_odict(index.row())
        if role == Qt.CheckStateRole:
            attr_key = odict.get(ODictAttr.odict_checked_attr.name)
            if attr_key:
                return odict.get(attr_key)
        elif role == Qt.DisplayRole:
            attr_key_names = odict.get(ODictAttr.odict_display_attrs.name, [])
            display_str = join_odict_values(odict, attr_key_names)
            return display_str
        elif role == Qt.DecorationRole:
            attr_key = odict.get(ODictAttr.odict_decoration_attr.name)
            if attr_key:
                color_str = odict.get(attr_key)
                color = QColor(color_str)
                return color
        elif role == Qt.BackgroundRole:
            attr_key = odict.get(ODictAttr.odict_background_attr.name)
            if attr_key:
                color_str = odict.get(attr_key)
                color = QColor(color_str)
                return color

    def add_odict(self, odict: ODict2):
        self.beginInsertRows(QModelIndex(), len(self.odicts), len(self.odicts))
        self.odicts.append(odict)
        self.endInsertRows()

    def delete_odict(self, odict_number: int):
        self.beginRemoveRows(QModelIndex(), odict_number, odict_number)
        del self.odicts[odict_number]
        self.endRemoveRows()

    def edit_odict(self, odict_number: int, new_odict: ODict2):
        odict_index = self.index(odict_number, 0, QModelIndex())
        odict = self.get_odict(odict_number)
        # if new odict has more or less attr keys then current odict
        # then it means that some rows must be removed and some must be inserted
        # so it is not just a dataChanged() event, it is remove-insert event sequence
        self.beginRemoveRows(odict_index, 0, len(odict) - 1)
        self.odicts[odict_index.row()] = {}
        self.endRemoveRows()
        self.beginInsertRows(odict_index, 0, len(new_odict) - 1)
        self.odicts[odict_index.row()] = new_odict
        self.endInsertRows()

    def get_odict(self, odict_number: int) -> ODict2:
        odict = self.odicts[odict_number]
        return odict

    def get_odicts(self):
        return self.odicts

    def get_attr_tuple(self, odict_number: int, attr_number: int):
        odict = self.get_odict(odict_number)
        attr_tuple = list(odict.items())[attr_number]
        return attr_tuple

    def get_attr_key(self, odict_number: int, attr_number: int):
        odict = self.get_odict(odict_number)
        attr_key = list(odict)[attr_number]
        return attr_key

    # def reset_odicts(self, odicts: typing.List[OrderedDict] = []):
    #     self.beginResetModel()
    #     self.odicts = odicts if odicts else []
    #     self.endResetModel()

    def add_attr(self, odict_numbers: typing.Iterable[int]):
        for odict_number in odict_numbers:
            odict_index = self.index(odict_number, 0, QModelIndex())
            attr_count = self.odict_new_attr_counter.get(odict_index.row(), 1)
            key = "key{}".format(attr_count)
            value = "value{}".format(attr_count)
            odict_tuple = (key, value)
            attr_count += 1
            self.odict_new_attr_counter[odict_index.row()] = attr_count
            odict = self.get_odict(odict_number)
            self.beginInsertRows(odict_index, len(odict), len(odict))
            odict.update([odict_tuple])
            self.endInsertRows()

    def delete_attr(self, odict_number: int, attr_number: int):
        parent = self.index(odict_number, 0, QModelIndex())
        odict = self.get_odict(odict_number)
        attr_key = list(odict)[attr_number]
        self.beginRemoveRows(parent, attr_number, attr_number)
        del odict[attr_key]
        self.endRemoveRows()

    def edit_attr(self, odict_number: int, attr_number: int, attr_value):
        odict = self.odicts[odict_number]
        attr_key = list(odict)[attr_number]
        odict[attr_key] = attr_value
        odict_index = self.index(odict_number, 0, QModelIndex())
        attr_index = self.index(attr_number, 1, odict_index)
        self.dataChanged.emit(attr_index, attr_index)

    def edit_attr_by_key(self, odict_number: int, attr_key: str, attr_value):
        odict = self.odicts[odict_number]
        odict_index = self.index(odict_number, 0)
        if attr_key in odict:
            odict[attr_key] = attr_value
            # we need to update all attr numbers but only one has changed!?
            self.dataChanged.emit(self.index(0, 0, odict_index), self.index(len(odict), 1, odict_index))
            # self.dataChanged.emit(odict_index, odict_index)
        else:
            self.beginInsertRows(odict_index, len(odict) + 1, len(odict) + 1)
            odict[attr_key] = attr_value
            self.endInsertRows()
