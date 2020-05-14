import sys
from collections import OrderedDict

from PyQt5.QtCore import QSize
from PyQt5.QtWidgets import QApplication, QMainWindow

from common_qt.message_handler import install_qt_message_handler
from deepable_qt.tree_view_config_deepable_tree_model import TreeViewConfigDeepableTreeModel
from slide_viewer.ui.odict.odict import ODict2, ODictModel
from slide_viewer.ui.odict.deep.templated_deepable_tree_widget import TemplatedDeepableTreeWidget
from src.test.odict._data import odict1

odicts = [
    ODict2(OrderedDict({
        ODictModel.odict_display_attrs: ["name_prop", "prop1"],
        ODictModel.odict_decoration_attr: "color_prop",
        ODictModel.odict_background_attr: "bg_prop",
        ODictModel.odict_hidden_attrs: ["prop1", "prop2"],
        ODictModel.odict_checked_attr: None,
        "name_prop": "name1",
        "color_prop": "red",
        "bg_prop": "lightgray",
        "prop1": "1",
        "prop2": "2",
    })),
    ODict2(OrderedDict({
        ODictModel.odict_display_attrs: ["name_prop", "prop1", "prop2", "prop3"],
        ODictModel.odict_decoration_attr: "color_prop",
        ODictModel.odict_background_attr: "bg_prop",
        ODictModel.odict_hidden_attrs: ["prop1", "prop2", "prop3", "color_prop", "bg_prop", "name_prop"],
        ODictModel.odict_checked_attr: None,
        "name_prop": "name1",
        "color_prop": "red",
        "bg_prop": "lightblue",
        "prop1": "1",
        "prop2": "2",
        "prop3": "3",
    })),
    ODict2(OrderedDict({
        ODictModel.odict_display_attrs: ["color_prop"],
        ODictModel.odict_decoration_attr: "color_prop",
        ODictModel.odict_background_attr: None,
        ODictModel.odict_hidden_attrs: [],
        ODictModel.odict_checked_attr: None,
        "name_prop": "name1",
        "color_prop": "red",
    }))
]

template_odicts = [
    ODict2(OrderedDict({
        ODictModel.odict_display_attrs: ["name_prop", "prop1"],
        ODictModel.odict_decoration_attr: "color_prop",
        ODictModel.odict_background_attr: "bg_prop",
        ODictModel.odict_hidden_attrs: [],
        ODictModel.odict_checked_attr: "default",
        "name_prop": "name1",
        "color_prop": "red",
        "bg_prop": "lightgreen",
        "default": False,
    })),
    ODict2(OrderedDict({
        ODictModel.odict_display_attrs: ["name_prop", "prop1"],
        ODictModel.odict_decoration_attr: "color_prop",
        ODictModel.odict_background_attr: None,
        ODictModel.odict_hidden_attrs: None,
        ODictModel.odict_checked_attr: "default",
        "name_prop": "name2",
        "color_prop": "red",
        "default": True,
        "prop1": "1",
    })),
]

# if __name__ == "__main__":
#     install_qt_message_handler()
#     app = QApplication(sys.argv)
#     window = QMainWindow()
#     widget = TemplatedDeepableTreeWidget(window)
#     # widget.templates_view.setModel(
#     #     ODictsTreeModel(template_odicts, [], ODictsTreeModelSelectMode.odict_rows, "default"))
#     instances_model = DeepableTreeModel(headers=("Items", ""))
#     instances_model.set_root(odict1)
#     widget.instances_view.setModel(instances_model)
#
#     window.setCentralWidget(widget)
#
#     window.show()
#     window.resize(QSize(700, 700))
#     sys.exit(app.exec_())
