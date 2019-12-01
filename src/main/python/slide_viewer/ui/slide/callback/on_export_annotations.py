from typing import Dict

from PyQt5.QtCore import QFileInfo, QFile

from slide_viewer.common import file_utils
from slide_viewer.ui.common.action.select_json_file_action import SelectJsonFileAction
from slide_viewer.ui.odict.deep.base.deepable import deep_items
from slide_viewer.ui.odict.deep.deepable_tree_view import DeepableTreeView
from slide_viewer.ui.odict.deep.model import AnnotationModel, AnnotationTreeItems


def on_export_annotations(view: DeepableTreeView, slide_path: str) -> None:
    def on_select_file(file_path: str) -> None:
        model = view.model().get_root()
        annotations: Dict[str, AnnotationModel] = dict(deep_items(model))
        annotations_container = AnnotationTreeItems(annotations=annotations)
        file_utils.write(file_path, annotations_container.json(indent=2))

    slide_name = QFileInfo(QFile(slide_path)).baseName()
    default_file_name = f"{slide_name}_annotations"
    select_image_file_action = SelectJsonFileAction("internal", view, on_select_file, default_file_name)
    select_image_file_action.trigger()
