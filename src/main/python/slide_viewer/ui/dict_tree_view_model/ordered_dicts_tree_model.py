import json
import typing
from collections import OrderedDict
from enum import Enum

from PyQt5.QtCore import Qt, QAbstractItemModel, QObject, QModelIndex
from PyQt5.QtGui import QColor, QBrush

JSON_ROLE = Qt.UserRole + 1


class StandardAttrKey(Enum):
    name = 1
    annotation_type = 2
    points = 3
    pen_color = 4
    text_background_color = 5
    area = 6


# hidden_standard_attr_keys = set(StandardAttrKey.annotation_type, StandardAttrKey.points)
readonly_standard_attr_keys = set(
    [StandardAttrKey.annotation_type.name, StandardAttrKey.points.name, StandardAttrKey.area.name])
standard_attr_keys = set(attr.name for attr in StandardAttrKey)


def is_standard_attr_key(attr_key: str):
    return attr_key in standard_attr_keys


class OrderedDictsTreeModel(QAbstractItemModel):

    def __init__(self, odicts: typing.List[OrderedDict] = [], parent: typing.Optional[QObject] = None) -> None:
        super().__init__(parent)
        self.odicts = odicts if odicts else []
        # https://www.riverbankcomputing.com/pipermail/pyqt/2007-April/015842.html
        # Qt requires method "parent(self, index: QModelIndex) -> QModelIndex"
        # To find out parent of index, we need to store info about parent in index.
        # "internalPointer" is the place were we can store info about parent.
        # The problems with "internalPointer" are:
        # 1) we cant store integer because it would be interpreted as address and program will crash
        # 2) we can store object in it, but we need to keep reference to this object because qt will not
        self.pyqt_bug_weak_ref_dict = dict()
        self.odict_new_attr_counter = {}
        self.column_headers = ["Name", "Value"]

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
            return
        if self.is_attr(index):
            return self.data_attr(index, role)
        elif self.is_dict(index):
            return self.data_odict(index, role)
        return

    def setData(self, index: QModelIndex, value: typing.Any, role: int = ...) -> bool:
        if self.is_attr_value(index) and role == Qt.EditRole:
            self.edit_attr(index.parent().row(), index.row(), value)
            return True
        return super().setData(index, value, role)

    @staticmethod
    def is_attr(index: QModelIndex):
        return index.isValid() and index.parent().isValid()

    @staticmethod
    def is_attr_key(index: QModelIndex):
        return OrderedDictsTreeModel.is_attr(index) and index.column() == 0

    @staticmethod
    def is_standard_attr_key(index: QModelIndex):
        return OrderedDictsTreeModel.is_attr_key(index) and is_standard_attr_key(index.data(Qt.DisplayRole))

    @staticmethod
    def is_attr_value(index: QModelIndex):
        return OrderedDictsTreeModel.is_attr(index) and index.column() == 1

    @staticmethod
    def is_dict(index: QModelIndex):
        return index.isValid() and not index.parent().isValid()

    def flags(self, index: QModelIndex) -> Qt.ItemFlags:
        # only attr values are editable because keys have order position inside OrderedDict
        # if you want to rename attr key, you have choices:
        # - edit dict fully (like in "Edit as JSON" action)
        # - delete old key and add new key
        attr_key = self.index(index.row(), 0, index.parent()).data()
        if OrderedDictsTreeModel.is_attr_value(index) and attr_key not in readonly_standard_attr_keys:
            return super().flags(index) | Qt.ItemIsEditable
        else:
            return super().flags(index)

    def data_attr(self, index: QModelIndex, role: int = Qt.DisplayRole):
        odict: OrderedDict = self.odicts[index.parent().row()]
        if role == Qt.DisplayRole or role == Qt.EditRole:
            odict_tuple = list(odict.items())[index.row()]
            odict_tuple_value = odict_tuple[index.column()]
            return odict_tuple_value

    def data_odict(self, index: QModelIndex, role: int = Qt.DisplayRole):
        if index.column() == 0:
            odict: OrderedDict = self.odicts[index.row()]
            if role == Qt.DisplayRole:
                return odict.get(StandardAttrKey.name.name)
            elif role == Qt.DecorationRole:
                return QColor(odict.get(StandardAttrKey.pen_color.name))
            elif role == JSON_ROLE:
                return json.dumps(odict, indent=2)
            # elif role == Qt.BackgroundRole:
            #     return QBrush(QColor(169, 204, 169, 200))

    def add_odict(self, odict: OrderedDict):
        self.beginInsertRows(QModelIndex(), len(self.odicts), len(self.odicts))
        self.odicts.append(odict)
        self.endInsertRows()

    def delete_odict(self, odict_number: int):
        self.beginRemoveRows(QModelIndex(), odict_number, odict_number)
        del self.odicts[odict_number]
        self.endRemoveRows()

    def edit_odict(self, odict_number: int, new_odict: OrderedDict):
        odict_index = self.index(odict_number, 0, QModelIndex())
        odict = self.odicts[odict_index.row()]
        # if new odict has more or less attr keys then current odict
        # then it means that some rows must be removed and some must be inserted
        # so it is not just a dataChanged() event, it are remove-insert events
        self.beginRemoveRows(odict_index, 0, len(odict) - 1)
        self.odicts[odict_index.row()] = {}
        self.endRemoveRows()
        self.beginInsertRows(odict_index, 0, len(new_odict) - 1)
        self.odicts[odict_index.row()] = new_odict
        self.endInsertRows()

    # def reset_odicts(self, odicts: typing.List[OrderedDict] = []):
    #     self.beginResetModel()
    #     self.odicts = odicts if odicts else []
    #     self.endResetModel()

    # TODO may be useful to add some common attr key to all odicts at once (like 'tag', 'comments')
    def add_attr(self, odict_numbers: typing.Iterable[int]):
        for odict_number in odict_numbers:
            odict_index = self.index(odict_number, 0, QModelIndex())
            odict = self.odicts[odict_index.row()]
            attr_count = self.odict_new_attr_counter.get(odict_index.row(), 1)
            key = "key{}".format(attr_count)
            value = "value{}".format(attr_count)
            odict_tuple = (key, value)
            attr_count += 1
            self.odict_new_attr_counter[odict_index.row()] = attr_count
            self.beginInsertRows(odict_index, len(odict), len(odict))
            odict.update([odict_tuple])
            self.endInsertRows()

    def delete_attr(self, odict_number: int, attr_number: int):
        parent = self.index(odict_number, 0, QModelIndex())
        odict = self.odicts[parent.row()]
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
