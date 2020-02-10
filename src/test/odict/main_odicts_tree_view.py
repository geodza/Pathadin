import sys

from PyQt5.QtCore import QSize, Qt
from PyQt5.QtWidgets import QApplication, QMainWindow

from slide_viewer.common_qt.message_handler import install_qt_message_handler
from slide_viewer.common_qt.persistent_settings.settings_utils import read_settings, write_settings
from slide_viewer.common_qt.persistent_settings.user_custom_color import get_user_custom_color_names, \
    set_user_custom_colors
from slide_viewer.ui.dict_tree_view_model.action.context_menu_factory import context_menu_factory2
from slide_viewer.ui.odict.odict import ODict3, ODictModel
from slide_viewer.ui.odict.odicts_tree_model import ODictsTreeModel, ODictsTreeModelSelectMode
from slide_viewer.ui.odict.deep.deepable_tree_view import DeepableTreeView

odicts = [
    ODictModel({
        ODictModel.odict_display_attrs: ["name_prop", "prop1"],
        ODictModel.odict_decoration_attr: "color_prop",
        ODictModel.odict_background_attr: "bg_prop",
        ODictModel.odict_hidden_attrs: ["prop1", "prop2", *getattr(ODict3, 'predefined_attrs')],
        ODictModel.odict_checked_attr: "checked_prop",
        "name_prop": "name1\nnewline\nname1",
        "color_prop": "red",
        "bg_prop": "lightgray",
        "checked_prop": True,
        "prop1": "1",
        "prop2": "2",
    }),
    ODictModel({
        ODictModel.odict_display_attrs: ["name_prop", "prop1", "prop2", "prop3"],
        ODictModel.odict_decoration_attr: "color_prop",
        ODictModel.odict_background_attr: "bg_prop",
        ODictModel.odict_hidden_attrs: ["prop1", "prop2", "prop3", "color_prop", "bg_prop", "name_prop"],
        ODictModel.odict_checked_attr: "checked_prop",
        "name_prop": "name1",
        "color_prop": "red",
        "bg_prop": "lightblue",
        "checked_prop": True,
        "prop1": "1",
        "prop2": "2",
        "prop3": "3",
    }),
    ODictModel({
        ODictModel.odict_display_attrs: ["color_prop"],
        ODictModel.odict_decoration_attr: "color_prop",
        ODictModel.odict_background_attr: None,
        ODictModel.odict_hidden_attrs: [],
        ODictModel.odict_checked_attr: "checked_prop",
        "name_prop": "name1",
        "color_prop": "red",
        "checked_prop": True,
    })
]

if __name__ == "__main__":
    install_qt_message_handler()
    app = QApplication(sys.argv)
    window = QMainWindow()
    model = ODictsTreeModel(odicts, [], ODictsTreeModelSelectMode.odict_rows, "checked_prop")
    view = DeepableTreeView(model, window)
    view.setContextMenuPolicy(Qt.CustomContextMenu)
    view.customContextMenuRequested.connect(context_menu_factory2(view))

    window.setCentralWidget(view)

    window.show()
    window.resize(QSize(700, 700))

    dict_ = read_settings("app1", "")
    set_user_custom_colors(dict_.get("user_custom_colors") or [])


    def on_about_to_quit():
        dict_ = {"user_custom_colors": get_user_custom_color_names()}
        write_settings("app1", "", dict_)

        # color = QColorDialog.getColor(Qt.white, window)


    app.aboutToQuit.connect(on_about_to_quit)
    sys.exit(app.exec_())
