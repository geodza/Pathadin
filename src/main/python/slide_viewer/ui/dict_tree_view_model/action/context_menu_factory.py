from PyQt5.QtCore import QPoint, QModelIndex, QItemSelectionModel
from PyQt5.QtWidgets import QAbstractItemView, QMenu

from slide_viewer.ui.common.my_action import MyAction
from slide_viewer.ui.dict_tree_view_model.action.attr_action_factory import add_attr_factory, clear_attrs_factory, \
    copy_attrs_factory, delete_attrs_factory
from slide_viewer.ui.dict_tree_view_model.action.odict_action_factory import duplicate_odicts_factory, \
    delete_odicts_factory, \
    edit_odict_as_json_factory, update_target_with_source_factory, make_template_factory, set_odict_default_factory
from slide_viewer.ui.dict_tree_view_model.ordered_dicts_tree_model import OrderedDictsTreeModel
from slide_viewer.ui.dict_tree_view_model.ordered_dicts_tree_view import OrderedDictsTreeView


def get_update_odict_mode_and_numbers(view: QAbstractItemView):
    indexes = view.selectionModel().selection().indexes()
    indexes = set(i.sibling(i.row(), 0) for i in indexes if OrderedDictsTreeModel.is_dict(i))
    if len(indexes) and not (len(indexes) == 1 and view.currentIndex() in indexes):
        update_mode, update_numbers = "selected", set(i.row() for i in indexes)
    else:
        update_mode, update_numbers = "all", range(view.model().rowCount())
    return update_mode, update_numbers


def get_attr_mode_and_numbers(view: QAbstractItemView):
    current_index = view.currentIndex()
    indexes = view.selectionModel().selection().indexes()
    if current_index.isValid() and view.selectionModel().isSelected(current_index):
        mode, numbers = "selected", {i.row(): i.parent().row() for i in indexes}
    elif current_index.isValid():
        mode, numbers = "current", {current_index.row(): current_index.parent().row()}
    else:
        mode, numbers = None, None
    return mode, numbers


def get_odict_mode_and_numbers(view: QAbstractItemView):
    current_index = view.currentIndex()
    indexes = view.selectionModel().selection().indexes()
    if current_index.isValid() and view.selectionModel().isSelected(current_index):
        mode, numbers = "selected", set(i.row() for i in indexes)
    elif current_index.isValid():
        mode, numbers = "current", [current_index.row()]
    else:
        mode, numbers = "all", range(view.model().rowCount())
    return mode, numbers


def add_odict_actions(menu: QMenu, view: OrderedDictsTreeView):
    model = view.model()
    mode, numbers = get_odict_mode_and_numbers(view)
    MyAction(f"Add attrs to {mode}", menu, add_attr_factory(numbers, model))
    MyAction(f"Remove non-standard attrs from {mode}", menu, clear_attrs_factory(numbers, model))
    MyAction(f"Duplicate {mode}", menu, duplicate_odicts_factory(numbers, model))
    MyAction(f"Delete {mode}", menu, delete_odicts_factory(numbers, model))
    if mode == 'current' or (mode == 'selected' and len(numbers) == 1):
        current_number = next(iter(numbers))
        menu.addSeparator()
        MyAction(f"Edit {mode} as JSON", menu, edit_odict_as_json_factory(current_number, model))
        current_index = view.currentIndex()
        current_number = current_index.row()
        update_mode, update_numbers = get_update_odict_mode_and_numbers(view)
        menu.addSeparator()
        update_func = update_target_with_source_factory(current_number, update_numbers,
                                                        model, model)
        MyAction(f"Update {update_mode} with current", menu, update_func)
        # we need override to have possibility to delete attr from all dicts at once
        override_func = update_target_with_source_factory(current_number, update_numbers,
                                                          model, model, True)
        MyAction(f"Override {update_mode} with current", menu, override_func)


def add_odict_instance_actions(menu: QMenu, instances_view: OrderedDictsTreeView, templates_view: OrderedDictsTreeView):
    instances_model, templates_model = instances_view.model(), templates_view.model()
    mode, numbers = get_odict_mode_and_numbers(instances_view)
    menu.addSeparator()
    MyAction(f"Make template(s) from {mode}", menu,
             make_template_factory(numbers, instances_model, templates_model))


def add_odict_template_actions(menu: QMenu, templates_view: OrderedDictsTreeView, instances_view: OrderedDictsTreeView):
    instances_model, templates_model = instances_view.model(), templates_view.model()
    mode, numbers = get_odict_mode_and_numbers(templates_view)
    menu.addSeparator()
    if mode == "current":
        current_index = templates_view.currentIndex()
        current_number = current_index.row()
        update_mode, update_numbers = get_update_odict_mode_and_numbers(instances_view)
        update_func = update_target_with_source_factory(current_number, update_numbers,
                                                        templates_model, instances_model)
        MyAction(f"Update {update_mode} instances with current template", menu, update_func)
        override_func = update_target_with_source_factory(current_number, update_numbers,
                                                          templates_model, instances_model, True)
        MyAction(f"Override {update_mode} instances with current template", menu, override_func)
        menu.addSeparator()
        MyAction(f"Set default", menu, set_odict_default_factory(current_number, templates_model))


def add_attr_template_actions(menu: QMenu, templates_view: OrderedDictsTreeView, instances_view: OrderedDictsTreeView):
    instances_model, templates_model = instances_view.model(), templates_view.model()
    mode, numbers = get_attr_mode_and_numbers(templates_view)
    menu.addSeparator()
    instance_mode, instance_numbers = get_odict_mode_and_numbers(instances_view)
    copy_func = copy_attrs_factory(numbers, instance_numbers, templates_model, instances_model)
    MyAction(f"Copy {mode} attribute(s) to {instance_mode} instance(s)", menu, copy_func)


def add_attr_actions(menu: QMenu, view: OrderedDictsTreeView):
    model = view.model()
    mode, numbers = get_attr_mode_and_numbers(view)
    update_mode, update_numbers = get_update_odict_mode_and_numbers(view)
    MyAction(f"Delete {mode} attr(s)", menu, delete_attrs_factory(numbers, model))
    copy_func = copy_attrs_factory(numbers, update_numbers, model, model)
    MyAction(f"Copy {mode} attribute to {update_mode}", menu, copy_func)


def context_menu_factory(instances_view: OrderedDictsTreeView, templates_view: OrderedDictsTreeView,
                         templates_view_is_source):
    def context_menu(position: QPoint):
        source_view = templates_view if templates_view_is_source else instances_view
        if not source_view.model().rowCount():
            return
        if not source_view.indexAt(position).isValid():
            source_view.setCurrentIndex(QModelIndex())
        if templates_view_is_source:
            instances_view.selectionModel().setCurrentIndex(QModelIndex(), QItemSelectionModel.NoUpdate)

        menu = QMenu()
        current_index = source_view.currentIndex()
        if OrderedDictsTreeModel.is_attr(current_index):
            add_attr_actions(menu, source_view)
            if templates_view_is_source:
                add_attr_template_actions(menu, templates_view, instances_view)
        elif OrderedDictsTreeModel.is_dict(current_index) or not current_index.isValid():
            add_odict_actions(menu, source_view)
            if templates_view_is_source:
                add_odict_template_actions(menu, templates_view, instances_view)
            else:
                add_odict_instance_actions(menu, instances_view, templates_view)

        menu.exec_(source_view.viewport().mapToGlobal(position))

    return context_menu
