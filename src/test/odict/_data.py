from collections import OrderedDict

from slide_viewer.ui.dict_tree_view_model.standard_attr_key import StandardAttrKey
from slide_viewer.ui.odict.odict import ODictModel
from slide_viewer.ui.odict.deep.model import TreeViewConfig, AnnotationModel
from slide_viewer.ui.slide.graphics.item.annotation.model import AnnotationGeometry
from slide_viewer.ui.model.annotation_type import AnnotationType

odict1 = OrderedDict({
    "odict1": OrderedDict({
        TreeViewConfig.snake_case_name: TreeViewConfig(display_attrs=["annotation.name", "color_prop"],
                                                       decoration_attr="color_prop"),
        "annotation": OrderedDict({
            StandardAttrKey.name.name: "annotation1",
            StandardAttrKey.annotation_type.name: AnnotationType.LINE,
            StandardAttrKey.length.name: 100,
            StandardAttrKey.origin_point.name: [(0, 0)],
            StandardAttrKey.points.name: [(0, 0), (10, 10)],
            StandardAttrKey.display_attr_keys.name: [StandardAttrKey.name.name, StandardAttrKey.area.name],
            StandardAttrKey.filter_id.name: "Filter1",
            StandardAttrKey.normed_hist.name: "?",
            StandardAttrKey.pixel_hist.name: "?",
            StandardAttrKey.pen_color.name: "red",
            StandardAttrKey.text_background_color.name: "green",
            TreeViewConfig.snake_case_name: TreeViewConfig(display_attrs=["name", "length"],
                                                           decoration_attr='pen_color'),
        }),
        "name_prop": "name1",
        "color_prop": "red",
        "checked_prop": True,
        "user_attrs": OrderedDict({
            "user_attr1": "val1",
            "odict42": OrderedDict({
                ODictModel.odict_display_attrs: ["name_prop", "color_prop"],
                ODictModel.odict_decoration_attr: "color_prop",
                ODictModel.odict_background_attr: None,
                ODictModel.odict_hidden_attrs: [ODictModel.odict_decoration_attr, "name_prop", "color_prop"],
                ODictModel.odict_checked_attr: "checked_prop",
                "name_prop": "name1",
                "color_prop": "red",
                "checked_prop": True,
                "odict42": OrderedDict({
                    ODictModel.odict_display_attrs: ["name_prop", "color_prop"],
                    ODictModel.odict_decoration_attr: "color_prop",
                    ODictModel.odict_background_attr: None,
                    ODictModel.odict_hidden_attrs: [ODictModel.odict_decoration_attr, "name_prop", "color_prop"],
                    ODictModel.odict_checked_attr: "checked_prop",
                    "name_prop": "name1",
                    "color_prop": "red",
                    "checked_prop": True,
                })
            })
        }),
    }),
    "odict2": OrderedDict({
        ODictModel.odict_display_attrs: ["name_prop", "bg_prop"],
        ODictModel.odict_decoration_attr: None,
        ODictModel.odict_background_attr: "bg_prop",
        ODictModel.odict_hidden_attrs: [],
        ODictModel.odict_checked_attr: "checked_prop",
        "name_prop": "name1",
        "bg_prop": "lightblue",
        "checked_prop": True,
    }),
    "odict3": OrderedDict({
        ODictModel.odict_display_attrs: ["name_prop", "checked_prop"],
        ODictModel.odict_decoration_attr: None,
        ODictModel.odict_background_attr: None,
        ODictModel.odict_hidden_attrs: None,
        ODictModel.odict_checked_attr: "checked_prop",
        "name_prop": "name1",
        "checked_prop": True,
    }),
    "odict4": OrderedDict({
        ODictModel.odict_display_attrs: ["name_prop", "checked_prop"],
        ODictModel.odict_decoration_attr: None,
        ODictModel.odict_background_attr: None,
        ODictModel.odict_hidden_attrs: None,
        ODictModel.odict_checked_attr: "checked_prop",
        "name_prop": "name1",
        "checked_prop": True,
    }),
    'annotation47': AnnotationModel(
        tree_view_config=TreeViewConfig(display_attrs=['id', 'figure_graphics_view_config.color'],
                                        decoration_attr='figure_graphics_view_config.color'),
        geometry=AnnotationGeometry(annotation_type=AnnotationType.LINE, origin_point=(0, 0),
                                    points=[(0, 0), (500, 500)]),
        id='1',
        label="annotation47"
    ),
    'annotation48': AnnotationModel(
        tree_view_config=TreeViewConfig(display_attrs=['label'], decoration_attr='figure_graphics_view_config.color'),
        geometry=AnnotationGeometry(annotation_type=AnnotationType.LINE, origin_point=(0, 0),
                                    points=[(0, 0), (200, 200)]),
        id='2',
        label="annotation48"
    ),
})
