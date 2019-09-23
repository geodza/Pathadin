import sys

from PyQt5.QtCore import QSize
from PyQt5.QtWidgets import QApplication

from slide_viewer.ui.dict_tree_view_model.config import is_instance_selectable, is_instance_editable, \
    is_template_selectable, is_template_editable, odict_background, create_instances_model
from slide_viewer.ui.dict_tree_view_model.ordered_dicts_tree_model import OrderedDictsTreeModel
from slide_viewer.ui.dict_tree_view_model.ordered_dicts_tree_widget import OrderedDictsTreeWidget
from slide_viewer.ui.dict_tree_view_model.standard_attr_key import readonly_standard_attr_keys, StandardAttrKey
from slide_viewer.ui.dict_tree_view_model.test_data import templates_data, instances_data


def excepthook(excType, excValue, tracebackobj):
    print(excType, excValue, tracebackobj)


sys.excepthook = excepthook

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = OrderedDictsTreeWidget()
    model = create_instances_model(instances_data)
    window.instances_view.setModel(model)

    templates_model = create_instances_model(templates_data)
    window.templates_view.setModel(templates_model)

    window.show()
    window.resize(QSize(500, 700))
    sys.exit(app.exec_())
