import sys
from collections import OrderedDict

from PyQt5.QtCore import QSize
from PyQt5.QtWidgets import QApplication, QMainWindow

from slide_viewer.ui.odict.odict import ODict2, ODictAttr
from slide_viewer.ui.odict.odicts_tree_model import ODictsTreeModel, ODictsTreeModelSelectMode
from slide_viewer.ui.odict.odicts_tree_view import ODictsTreeView


def excepthook(excType, excValue, tracebackobj):
    print(excType, excValue, tracebackobj)


odicts = [
    ODict2(OrderedDict({
        ODictAttr.odict_display_attrs.name: ["name_prop", "prop1"],
        ODictAttr.odict_decoration_attr.name: "color_prop",
        ODictAttr.odict_background_attr.name: "bg_prop",
        ODictAttr.odict_hidden_attrs.name: ["prop1", "prop2"],
        ODictAttr.odict_checked_attr.name: "checked_prop",
        "name_prop": "name1",
        "color_prop": "red",
        "bg_prop": "lightgray",
        "checked_prop": True,
        "prop1": "1",
        "prop2": "2",
    })),
    ODict2(OrderedDict({
        ODictAttr.odict_display_attrs.name: ["name_prop", "prop1", "prop2", "prop3"],
        ODictAttr.odict_decoration_attr.name: "color_prop",
        ODictAttr.odict_background_attr.name: "bg_prop",
        ODictAttr.odict_hidden_attrs.name: [],
        ODictAttr.odict_checked_attr.name: "checked_prop",
        "name_prop": "name1",
        "color_prop": "red",
        "bg_prop": "lightblue",
        "checked_prop": False,
        "prop1": "1",
        "prop2": "2",
        "prop3": "3",
    }))
]

sys.excepthook = excepthook

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = QMainWindow()
    model = ODictsTreeModel(odicts, [], ODictsTreeModelSelectMode.odict_rows, "checked_prop")
    view = ODictsTreeView(window)
    view.setModel(model)
    window.setCentralWidget(view)

    window.show()
    window.resize(QSize(500, 700))
    sys.exit(app.exec_())
