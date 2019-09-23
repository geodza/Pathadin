import copy
import json
from collections import OrderedDict

from slide_viewer.ui.common.edit_text_dialog import EditTextDialog
from slide_viewer.ui.dict_tree_view_model.ordered_dict_convert import to_primitive_odict, from_primitive_odict
from slide_viewer.ui.dict_tree_view_model.ordered_dicts_tree_model import OrderedDictsTreeModel
from slide_viewer.ui.dict_tree_view_model.standard_attr_key import is_standard_attr_key, StandardAttrKey, \
    attrs_not_to_copy


def delete_odicts_factory(odict_numbers: list, model: OrderedDictsTreeModel):
    def delete_odicts():
        for odict_number in reversed(sorted(odict_numbers)):
            model.delete_odict(odict_number)

    return delete_odicts


def duplicate_odicts_factory(odict_numbers: list, model: OrderedDictsTreeModel):
    def duplicate_odicts():
        new_odicts = []
        for odict_number in sorted(odict_numbers):
            odict = model.get_odict(odict_number)
            duplicate_odict = copy.deepcopy(odict)
            new_odicts.append(duplicate_odict)
        for new_odict in new_odicts:
            model.add_odict(new_odict)

    return duplicate_odicts


def make_template_factory(odict_numbers: list, source_model: OrderedDictsTreeModel,
                          target_model: OrderedDictsTreeModel):
    def make_template():
        for odict_number in sorted(odict_numbers):
            odict = source_model.get_odict(odict_number)
            odict_copy = copy.deepcopy(odict)
            odict_copy[StandardAttrKey.display_attr_keys.name] = [StandardAttrKey.name.name]
            odict_copy.pop(StandardAttrKey.points.name, None)
            odict_copy.pop(StandardAttrKey.area.name, None)
            odict_copy.pop(StandardAttrKey.length.name, None)
            odict_copy.pop(StandardAttrKey.annotation_type.name, None)
            if target_model.rowCount():
                odict_copy[StandardAttrKey.default_template.name] = False
            else:
                odict_copy[StandardAttrKey.default_template.name] = True
            # source_model.delete_odict(odict_number)
            target_model.add_odict(odict_copy)

    return make_template


def update_target_with_source_factory(source_odict_number: int, target_odict_numbers: list,
                                      source_model: OrderedDictsTreeModel,
                                      target_model: OrderedDictsTreeModel, override=False):
    def update_target():
        source_odict = source_model.get_odict(source_odict_number)
        for target_odict_number in target_odict_numbers:
            source_odict_copy = copy.deepcopy(source_odict)
            for attr_key in attrs_not_to_copy:
                source_odict_copy.pop(attr_key, None)
            target_odict = target_model.get_odict(target_odict_number)
            if override:
                target_odict = {key: value for key, value in target_odict.items() if is_standard_attr_key(key)}
            target_odict.update(source_odict_copy)
            target_model.edit_odict(target_odict_number, target_odict)

    return update_target


def set_odict_default_factory(odict_number: int, model: OrderedDictsTreeModel):
    def set_odict_default():
        model.edit_attr_by_key(odict_number, StandardAttrKey.default_template.name, True)

    return set_odict_default


def edit_odict_as_json_factory(odict_number: int, model: OrderedDictsTreeModel):
    def edit_as_json():
        odict = model.get_odict(odict_number)
        primitive_odict = to_primitive_odict(odict)
        odict_json = json.dumps(primitive_odict, indent=2)
        dialog = EditTextDialog(odict_json)

        def edit_odict():
            new_primitive_odict_json = dialog.text_editor.toPlainText()
            new_primitive_odict = OrderedDict(json.loads(new_primitive_odict_json))
            new_qt_odict = from_primitive_odict(new_primitive_odict)
            model.edit_odict(odict_number, new_qt_odict)

        dialog.accepted.connect(edit_odict)
        dialog.show()

    return edit_as_json
