from collections import OrderedDict

from PyQt5.QtGui import QColor

from slide_viewer.ui.dict_tree_view_model.standard_attr_key import StandardAttrKey

templates_data = [
    OrderedDict({
        'name': 'template1',
        'pen_color': QColor("red"),
        'tag': 'A',
        'default_template': False,
        StandardAttrKey.display_attr_keys.name: [StandardAttrKey.name.name],
    }),
    OrderedDict({
        'name': 'template2',
        'pen_color': QColor("yellow"),
        'text_background_color': QColor("yellow"),
        'comment': 'some user comment',
        'default_template': True,
        StandardAttrKey.display_attr_keys.name: [StandardAttrKey.name.name],
    }),
    OrderedDict({
        'name': 'template1',
        'pen_color': QColor("green"),
        'tag': 'A',
        'default_template': False,
        StandardAttrKey.display_attr_keys.name: [StandardAttrKey.name.name],
    }),
    OrderedDict({
        'name': 'template2',
        'pen_color': QColor("blue"),
        'text_background_color': QColor("yellow"),
        'comment': 'some user comment',
        'default_template': False,
        StandardAttrKey.display_attr_keys.name: [StandardAttrKey.name.name],
    }),
]
instances_data = [
    OrderedDict({
        'name': 'annotation1',
        'area': "100",
        'pen_color': QColor("red"),
        'tag': 'A',
        'ui_attrs_hidden': False,
        StandardAttrKey.display_attr_keys.name: [StandardAttrKey.name.name],
    }),
    OrderedDict({
        'name': 'annotation2',
        'area': "200",
        'pen_color': QColor("blue"),
        'tag': 'B',
        'ui_attrs_hidden': True,
        StandardAttrKey.display_attr_keys.name: [StandardAttrKey.name.name],
    }),
    OrderedDict({
        'name': 'annotation3',
        'area': "300",
        'pen_color': QColor("green"),
        'tag': 'C',
        'ui_attrs_hidden': False,
        StandardAttrKey.display_attr_keys.name: [StandardAttrKey.name.name],
    })
]
