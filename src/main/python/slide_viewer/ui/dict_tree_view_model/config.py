import copy
from collections import OrderedDict

from PyQt5.QtCore import QModelIndex, Qt
from PyQt5.QtGui import QColor

from slide_viewer.ui.dict_tree_view_model.ordered_dicts_tree_model import OrderedDictsTreeModel
from slide_viewer.ui.dict_tree_view_model.standard_attr_key import readonly_standard_attr_keys, StandardAttrKey


def is_instance_selectable(index: QModelIndex):
    return OrderedDictsTreeModel.is_dict(index)


def is_instance_editable(index: QModelIndex):
    attr_key_index = index.sibling(index.row(), 0)
    attr_key = attr_key_index.data(Qt.DisplayRole)
    attr_key_readonly = attr_key in readonly_standard_attr_keys
    is_editable = OrderedDictsTreeModel.is_attr_value(index) and not attr_key_readonly
    # print(attr_key, attr_key_readonly, is_editable)
    return is_editable


def is_template_selectable(index: QModelIndex):
    return OrderedDictsTreeModel.is_attr(index)


def is_template_editable(index: QModelIndex):
    return OrderedDictsTreeModel.is_attr_value(index)


def odict_background(index: QModelIndex):
    odict = index.model().get_odict(index.row())
    if odict.get(StandardAttrKey.default_template.name, None):
        return QColor("lightsteelblue")


def create_instances_model(odicts: list):
    model = OrderedDictsTreeModel(odicts, readonly_standard_attr_keys,
                                  StandardAttrKey.pen_color.name, None, is_instance_selectable,
                                  is_instance_editable)
    return model


def create_templates_model(odicts: list):
    model = OrderedDictsTreeModel(odicts, readonly_standard_attr_keys,
                                  StandardAttrKey.pen_color.name,
                                  odict_background,
                                  is_template_selectable, is_template_editable)
    return model


class Sequence:
    last_number = 0

    @staticmethod
    def next_number():
        Sequence.last_number += 1
        return Sequence.last_number


default_instance_odict = OrderedDict({
    StandardAttrKey.name.name: "",
    StandardAttrKey.pen_color.name: QColor("chartreuse"),
    StandardAttrKey.text_background_color.name: QColor("chartreuse"),
    StandardAttrKey.ui_attrs_hidden.name: False,
    StandardAttrKey.points.name: [],
    StandardAttrKey.annotation_type.name: None,
    StandardAttrKey.text_hidden.name: False,
    StandardAttrKey.display_attr_keys.name: [StandardAttrKey.name.name],
})


def create_default_instance_odict(odict_template=default_instance_odict):
    odict = copy.deepcopy(odict_template)
    return odict
