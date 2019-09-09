import json
import typing
from collections import OrderedDict

from PyQt5.QtCore import Qt, QModelIndex, QMargins, QPoint
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QMenu

from slide_viewer.ui.dict_tree_view_model.ordered_dicts_tree_model import OrderedDictsTreeModel, JSON_ROLE
from slide_viewer.ui.dict_tree_view_model.ordered_dicts_tree_view import OrderedDictsTreeView
from slide_viewer.ui.common.edit_text_dialog import EditTextDialog
from slide_viewer.ui.common.my_action import MyAction


class OrderedDictsTreeWidget(QWidget):

    def __init__(self, parent: typing.Optional[QWidget] = None) -> None:
        super().__init__(parent)

        self.view = OrderedDictsTreeView(self)
        self.view.setModel(OrderedDictsTreeModel([]))
        self.view.setContextMenuPolicy(Qt.CustomContextMenu)
        self.view.customContextMenuRequested.connect(self.on_context_menu)

        layout = QVBoxLayout()
        layout.addWidget(self.view)
        layout.setContentsMargins(QMargins())
        self.setLayout(layout)

    def on_context_menu(self, position: QPoint):
        index = self.view.currentIndex()
        if OrderedDictsTreeModel.is_attr(index) and not OrderedDictsTreeModel.is_standard_attr_key(index):
            self.on_attr_context_menu(position, index)
        elif OrderedDictsTreeModel.is_dict(index):
            self.on_dict_context_menu(position, index)

    def on_attr_context_menu(self, position: QPoint, index: QModelIndex):
        def delete_attr():
            self.view.model().delete_attr(index.parent().row(), index.row())

        menu = QMenu()
        menu.addAction(MyAction("Delete attribute", menu, delete_attr))
        menu.exec_(self.view.viewport().mapToGlobal(position))

    def on_dict_context_menu(self, position: QPoint, index: QModelIndex):
        def delete_dict():
            self.view.model().delete_odict(index.row())

        def add_attr():
            self.view.model().add_attr([index.row()])

        def edit_as_json():
            dict_json = index.data(JSON_ROLE)
            dialog = EditTextDialog(dict_json, self)

            def edit_dict():
                new_dict_json = dialog.text_editor.toPlainText()
                new_dict = OrderedDict(json.loads(new_dict_json))
                self.view.model().edit_odict(index.row(), new_dict)

            dialog.accepted.connect(edit_dict)
            dialog.show()

        menu = QMenu()
        menu.addAction(MyAction("Add attribute", menu, add_attr))
        menu.addAction(MyAction("Edit as JSON", menu, edit_as_json))
        menu.addAction(MyAction("Delete", menu, delete_dict))
        menu.exec_(self.view.viewport().mapToGlobal(position))
