import copy
from collections import OrderedDict

from slide_viewer.ui.dict_tree_view_model.ordered_dicts_tree_model import OrderedDictsTreeModel
from slide_viewer.ui.dict_tree_view_model.standard_attr_key import is_standard_attr_key, StandardAttrKey, \
    attrs_not_to_copy


def add_attr_factory(odict_numbers: list, model: OrderedDictsTreeModel):
    def add_attr():
        model.add_attr(odict_numbers)

    return add_attr


def delete_attrs_factory(attr_numbers: dict, model: OrderedDictsTreeModel):
    attr_numbers = OrderedDict(reversed(sorted(attr_numbers.items())))

    def delete_attr():
        for attr_number, odict_number in attr_numbers.items():
            attr_tuple = model.get_attr_tuple(odict_number, attr_number)
            attr_key = attr_tuple[0]
            # if is_standard_attr_key(attr_key):
            #     continue
            model.delete_attr(odict_number, attr_number)

    return delete_attr


def clear_attrs_factory(odict_numbers: list, model: OrderedDictsTreeModel):
    def clear_attrs():
        for odict_number in odict_numbers:
            odict = model.get_odict(odict_number)
            standard_attrs_odict = {key: value for key, value in odict.items() if is_standard_attr_key(key)}
            model.edit_odict(odict_number, standard_attrs_odict)

    return clear_attrs


def copy_attrs_factory(source_attr_numbers: dict, target_odict_numbers: list,
                       source_model: OrderedDictsTreeModel, target_model: OrderedDictsTreeModel):
    def copy_attrs():
        for source_attr_number, source_odict_number in sorted(source_attr_numbers.items()):
            source_odict_tuple = source_model.get_attr_tuple(source_odict_number, source_attr_number)
            if source_odict_tuple[0] in attrs_not_to_copy:
                continue
            for target_odict_number in target_odict_numbers:
                target_odict = target_model.get_odict(target_odict_number)
                target_odict.update([copy.deepcopy(source_odict_tuple)])
                target_model.edit_odict(target_odict_number, target_odict)

    return copy_attrs
