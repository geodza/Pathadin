import copy
import json
from typing import Tuple, List

from PyQt5.QtCore import QPoint, QModelIndex
from PyQt5.QtWidgets import QAbstractItemView, QMenu

from slide_viewer.ui.common.action.my_action import MyAction
from slide_viewer.ui.common.dialog.edit_text_dialog import EditTextDialog
from slide_viewer.ui.odict.deep.base.deepable import CommonJSONEncoder, common_object_pairs_hook, is_deepable, deep_keys, \
    deep_get, deep_set
from slide_viewer.ui.odict.deep.deepable_tree_view import DeepableTreeView


def get_update_mode_and_indexes(view: QAbstractItemView):
    current = view.currentIndex()
    selected = view.selectionModel().selection().indexes()
    selected_toplevel = [i for i in selected if i.column() == 0 and not i.parent().isValid()]
    if len(selected_toplevel) and not (len(selected_toplevel) == 1 and current in selected_toplevel):
        update_mode, update_indexes = "selected", list(selected_toplevel)
    else:
        update_mode, update_indexes = "all", [view.model().index(row, 0) for row in range(view.model().rowCount())]
    return update_mode, update_indexes


def get_mode_and_indexes(view: QAbstractItemView) -> Tuple[str, List[QModelIndex]]:
    current_index = view.currentIndex()
    selected_indexes = [i for i in view.selectionModel().selection().indexes() if i.column() == 0]
    if current_index.isValid() and view.selectionModel().isSelected(current_index):
        mode, indexes = "selected", list(selected_indexes)
    elif current_index.isValid():
        mode, indexes = "current", [current_index]
    else:
        mode, indexes = "all", [view.model().index(row, 0) for row in range(view.model().rowCount())]
    parent_index_ids = set(id(i.parent()) for i in indexes)
    indexes = [i for i in indexes if id(i) not in parent_index_ids]
    return mode, indexes


def context_menu_factory2(view: DeepableTreeView):
    def on_context_menu(position: QPoint):
        if not view.model().rowCount():
            return
        if not view.indexAt(position).isValid():
            view.setCurrentIndex(QModelIndex())

        menu = DeepableTreeViewMenuBuilder(view).build()

        menu.exec_(view.viewport().mapToGlobal(position))

    return on_context_menu


class DeepableTreeViewMenuBuilder:
    def __init__(self, view: DeepableTreeView) -> None:
        super().__init__()
        self.view = view
        self.model = view.model()
        self.mode, self.indexes = get_mode_and_indexes(view)
        self.current_number, self.current_index, self.update_mode, self.update_indexes = None, None, None, None
        if self.mode == 'current' or (self.mode == 'selected' and len(self.indexes) == 1):
            self.current_index = next(iter(self.indexes))
            #     self.current_index = self.model.index(self.current_number, 0)
            self.update_mode, self.update_indexes = get_update_mode_and_indexes(view)
        self.menu = QMenu()

    def build(self) -> QMenu:
        self.add_add_attr()
        self.add_duplicate()
        self.add_delete()
        if self.current_index is not None:
            self.add_separator()
            self.add_edit_as_json()
            self.add_separator()
            self.add_update()
        else:
            self.add_reset()
        return self.menu

    def add_separator(self):
        self.menu.addSeparator()

    def add_add_attr(self):
        menu, mode, indexes, model = self.menu, self.mode, self.indexes, self.model

        def f():
            for i in indexes:
                key = model.key(i)
                new_attr_key = f"{key}.attr_{model.rowCount(i)}"
                model[new_attr_key] = ""

        MyAction(f"Add new attr to {mode}", menu, f)

    def add_duplicate(self):
        menu, mode, indexes, model = self.menu, self.mode, self.indexes, self.model

        def f():
            for i in indexes:
                key = model.key(i)
                copy_key = f"{key}_{model.rowCount(i.parent())}"
                value = model[key]
                copy_value = copy.deepcopy(value)
                if 'id' in deep_keys(value):
                    deep_set(copy_value, 'id', copy_key)

                model[copy_key] = copy_value

        MyAction(f"Duplicate {mode}", menu, f)

    def add_delete(self):
        menu, mode, indexes, model = self.menu, self.mode, self.indexes, self.model

        def f():
            for i in indexes:
                key = model.key(i)
                del model[key]

        MyAction(f"Delete {mode}", menu, f)

    def add_edit_as_json(self):
        menu, mode, indexes, model, current_index = self.menu, self.mode, self.indexes, self.model, self.current_index

        def edit_as_json():
            key, value = model.key(current_index), model.value(current_index)
            odict_json = json.dumps(value, indent=2, cls=CommonJSONEncoder)
            dialog = EditTextDialog(odict_json)

            def edit_odict():
                new_json = dialog.text_editor.toPlainText()
                local_key = key.split('.')[-1]
                new_json_hack = f'{{"{local_key}":{new_json}}}'
                new_odict_hack = json.loads(new_json_hack, object_pairs_hook=common_object_pairs_hook)
                new_odict = new_odict_hack[local_key]
                # del model[key]
                # model.beginResetModel()
                model[key] = new_odict
                # model.endResetModel()

            dialog.accepted.connect(edit_odict)
            dialog.show()

        MyAction(f"Edit {mode} as JSON", menu, edit_as_json)

    def add_update(self):
        menu, mode, indexes, model, current_index, update_indexes, update_mode = \
            self.menu, self.mode, self.indexes, self.model, self.current_index, self.update_indexes, self.update_mode
        keys_to_ignore = set(['id', 'name'])

        def f():
            source_key, source_value = model.key(current_index), model.value(current_index)
            source_local_key = source_key.split('.', 1)[1:]
            for i in update_indexes:
                target_key = '.'.join([model.key(i)] + source_local_key)
                try:
                    source_value_copy = copy.deepcopy(source_value)
                    if is_deepable(source_value_copy):
                        for child_key in deep_keys(source_value_copy):
                            if child_key not in keys_to_ignore:
                                # It is like update method of dict. We do not override target value, but update it
                                model[target_key + '.' + child_key] = deep_get(source_value_copy, child_key)
                    else:
                        model[target_key] = source_value_copy
                except Exception as e:
                    # Target object hasn't appropriate structure.
                    # Try to update it with object in higher level.
                    # This occurs when you try to copy a.b.c to a1 which hasn't b, so you need to copy b first.
                    pass

        MyAction(f"Update {update_mode} with current", menu, f)

    def add_reset(self):
        def f():
            self.model.beginResetModel()
            self.model.endResetModel()

        MyAction(f"Reset model", self.menu, f)