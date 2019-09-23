from collections import OrderedDict

from PyQt5.QtGui import QColor

from slide_viewer.ui.dict_tree_view_model.standard_attr_key import StandardAttrKey
from slide_viewer.ui.slide.graphics.annotation.annotation_type import AnnotationType
from slide_viewer.ui.slide.graphics.annotation.annotation_utls import point_to_tuple, tuple_to_point


def to_primitive_odict(d: OrderedDict) -> OrderedDict:
    primitives_odict = OrderedDict()
    for attr_key, attr_value in d.items():
        if attr_key == StandardAttrKey.points.name:
            primitive_attr_value = tuple(map(point_to_tuple, attr_value))
        elif isinstance(attr_value, QColor):
            primitive_attr_value = attr_value.name()
        elif attr_key == StandardAttrKey.annotation_type.name:
            primitive_attr_value = attr_value.name
        else:
            primitive_attr_value = attr_value
        primitives_odict[attr_key] = primitive_attr_value
    return primitives_odict


def from_primitive_odict(d: OrderedDict) -> OrderedDict:
    qt_odict = OrderedDict()
    for attr_key, attr_value in d.items():
        if attr_key == StandardAttrKey.points.name:
            qt_value = tuple(map(tuple_to_point, attr_value))
        elif attr_key in set([StandardAttrKey.pen_color.name, StandardAttrKey.text_background_color.name]):
            qt_value = QColor(attr_value)
        elif attr_key == StandardAttrKey.annotation_type.name:
            qt_value = AnnotationType[attr_value]
        else:
            qt_value = attr_value
        qt_odict[attr_key] = qt_value
    return qt_odict
