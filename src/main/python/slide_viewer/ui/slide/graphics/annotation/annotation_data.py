from collections import OrderedDict

from slide_viewer.ui.dict_tree_view_model.standard_attr_key import StandardAttrKey


def odict_getter(i):
    return lambda self: self.odict[i.name]


def odict_setter(i):
    def setter(self, v):
        self.odict[i.name] = v

    return setter


def odict_prop(i):
    return property(odict_getter(i), odict_setter(i), None)


class AnnotationData:

    def __init__(self, odict=OrderedDict()) -> None:
        super().__init__()
        self.odict = odict

    name = odict_prop(StandardAttrKey.name)
    points = odict_prop(StandardAttrKey.points)
    pen_color = odict_prop(StandardAttrKey.pen_color)
    text_background_color = odict_prop(StandardAttrKey.text_background_color)
    annotation_type = odict_prop(StandardAttrKey.annotation_type)
    text_hidden = odict_prop(StandardAttrKey.text_hidden)
    length = odict_prop(StandardAttrKey.length)
    area = odict_prop(StandardAttrKey.area)
    display_attr_keys = odict_prop(StandardAttrKey.display_attr_keys)
    ui_attrs_hidden = odict_prop(StandardAttrKey.ui_attrs_hidden)
