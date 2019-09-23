import typing
from collections import OrderedDict

from PyQt5.QtCore import Qt, QAbstractItemModel, QObject, QModelIndex
from PyQt5.QtGui import QColor, QBrush

from slide_viewer.ui.common.common import join_odict_values
from slide_viewer.ui.dict_tree_view_model.standard_attr_key import StandardAttrKey


class OrderedDictsTreeModel(QAbstractItemModel):

    def __init__(self, odicts: typing.List[OrderedDict] = [], readonly_attr_keys=[],
                 odict_display_attr_keys=None, odict_decoration_attr_key=None, odict_background_func=None,
                 is_selectable_func=None, is_editable_func=None,
                 parent: typing.Optional[QObject] = None) -> None:
        super().__init__(parent)
        self.odicts = odicts if odicts else []
        self.readonly_attr_keys = readonly_attr_keys if readonly_attr_keys else []
        self.odict_display_attr_keys = odict_display_attr_keys
        self.odict_decoration_attr_key = odict_decoration_attr_key
        self.odict_background_func = odict_background_func
        self.is_selectable_func = is_selectable_func if is_selectable_func else lambda index: False
        self.is_editable_func = is_editable_func if is_editable_func else lambda index: False
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
        # print(f"setData {index} {value}")
        if self.is_attr_value(index) and role == Qt.EditRole:
            if isinstance(index.data(Qt.DisplayRole), QColor):
                value = QColor(value)
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
    def is_attr_value(index: QModelIndex):
        return OrderedDictsTreeModel.is_attr(index) and index.column() == 1

    @staticmethod
    def is_dict(index: QModelIndex):
        return index.isValid() and not index.parent().isValid()

    def flags(self, index: QModelIndex) -> Qt.ItemFlags:
        # only attr values are editable because keys have order position inside OrderedDict
        flags = super().flags(index)
        if self.is_selectable_func(index):
            flags |= Qt.ItemIsSelectable
        else:
            flags &= ~Qt.ItemIsSelectable
        if self.is_editable_func(index):
            flags |= Qt.ItemIsEditable
        else:
            flags &= ~Qt.ItemIsEditable
        return flags

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
                attr_key_names = odict.get(StandardAttrKey.display_attr_keys.name, [])
                display_str = join_odict_values(odict, attr_key_names)
                return display_str
                # return odict.get(self.odict_display_attr_key)
            elif role == Qt.DecorationRole:
                return odict.get(self.odict_decoration_attr_key)
            elif role == Qt.BackgroundRole and self.odict_background_func:
                return self.odict_background_func(index)

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
        # so it is not just a dataChanged() event, it is remove-insert event sequence
        self.beginRemoveRows(odict_index, 0, len(odict) - 1)
        self.odicts[odict_index.row()] = {}
        self.endRemoveRows()
        self.beginInsertRows(odict_index, 0, len(new_odict) - 1)
        self.odicts[odict_index.row()] = new_odict
        self.endInsertRows()

    def get_odict(self, odict_number: int):
        odict = self.odicts[odict_number]
        return odict

    def get_odicts(self):
        return self.odicts

    def get_attr_tuple(self, odict_number: int, attr_number):
        attr_tuple = list(self.odicts[odict_number].items())[attr_number]
        return attr_tuple

    # def reset_odicts(self, odicts: typing.List[OrderedDict] = []):
    #     self.beginResetModel()
    #     self.odicts = odicts if odicts else []
    #     self.endResetModel()

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

    def edit_attr_by_key(self, odict_number: int, attr_key: str, attr_value):
        odict = self.odicts[odict_number]
        odict_index = self.index(odict_number, 0)
        if attr_key in odict:
            odict[attr_key] = attr_value
            self.dataChanged.emit(odict_index, odict_index)
        else:
            self.beginInsertRows(odict_index, len(odict) + 1, len(odict) + 1)
            odict[attr_key] = attr_value
            self.endInsertRows()
