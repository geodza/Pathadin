from PyQt5.QtCore import QFileInfo, QFile

import json_utils
from slide_viewer.ui.common.select_json_file_action import SelectJsonFileAction
from slide_viewer.ui.dict_tree_view_model.config import create_instances_model
from slide_viewer.ui.dict_tree_view_model.ordered_dict_convert import from_primitive_odict
from slide_viewer.ui.dict_tree_view_model.ordered_dicts_tree_model import OrderedDictsTreeModel
from slide_viewer.ui.slide.widget.slide_viewer_widget import SlideViewerWidget


def on_import_annotations(widget: SlideViewerWidget):
    def on_select_file(file_path: str):
        widget.view.on_off_annotation_item()
        odicts = json_utils.read(file_path)
        qt_odicts = [from_primitive_odict(odict) for odict in odicts]
        model = create_instances_model(qt_odicts)
        widget.odicts_widget.instances_view.setModel(model)
        widget.view.reset_annotation_items(qt_odicts)

    if widget.slide_helper:
        slide_name = QFileInfo(QFile(widget.slide_helper.slide_path)).baseName()
        default_file_name = f"{slide_name}_annotations"
        select_image_file_action = SelectJsonFileAction("internal", widget, on_select_file, default_file_name, False)
        select_image_file_action.trigger()
