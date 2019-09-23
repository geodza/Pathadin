from enum import Enum


class StandardAttrKey(Enum):
    name = 1
    annotation_type = 2
    points = 3
    pen_color = 4
    text_background_color = 5
    area = 6
    length = 7
    text_hidden = 8
    default_template = 9
    display_attr_keys = 10
    ui_attrs_hidden = 11


# hidden_standard_attr_keys = set(StandardAttrKey.annotation_type, StandardAttrKey.points)
readonly_standard_attr_keys = set(
    [StandardAttrKey.annotation_type.name, StandardAttrKey.points.name, StandardAttrKey.area.name])
standard_attr_keys = set(attr.name for attr in StandardAttrKey)

ui_attr_keys = set([
    StandardAttrKey.annotation_type.name, StandardAttrKey.points.name, StandardAttrKey.pen_color.name,
    StandardAttrKey.text_background_color.name, StandardAttrKey.points.name, StandardAttrKey.text_hidden.name,
    StandardAttrKey.display_attr_keys.name
])

attrs_not_to_copy = set([StandardAttrKey.name.name, StandardAttrKey.area.name, StandardAttrKey.default_template.name])


def is_standard_attr_key(attr_key: str):
    return attr_key in standard_attr_keys
