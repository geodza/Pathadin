from PyQt5.QtCore import QFileInfo, QFile

import json_utils
from slide_viewer.ui.common.select_json_file_action import SelectJsonFileAction
from slide_viewer.ui.dict_tree_view_model.ordered_dict_convert import to_primitive_odict
from slide_viewer.ui.slide.widget.slide_viewer_widget import SlideViewerWidget


def on_export_annotations(widget: SlideViewerWidget):
    def on_select_file(file_path: str):
        odicts = widget.odicts_widget.instances_view.model().odicts
        primitive_odicts = [to_primitive_odict(odict) for odict in odicts]
        json_utils.write(file_path, primitive_odicts)

    if widget.slide_helper:
        slide_name = QFileInfo(QFile(widget.slide_helper.slide_path)).baseName()
        default_file_name = f"{slide_name}_annotations"
        select_image_file_action = SelectJsonFileAction("internal", widget, on_select_file, default_file_name)
        select_image_file_action.trigger()
