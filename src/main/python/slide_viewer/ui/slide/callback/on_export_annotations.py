from typing import Dict

from PyQt5.QtCore import QFileInfo, QFile

from slide_viewer.common import file_utils
from common_qt.select_json_file_action import SelectJsonFileAction
from slide_viewer.ui.odict.deep.model import AnnotationModel, AnnotationTreeItems
from slide_viewer.ui.slide.widget.interface.annotation_service import AnnotationService


def on_export_annotations(annotation_service: AnnotationService, slide_path: str) -> None:
    def on_select_file(file_path: str) -> None:
        annotations: Dict[str, AnnotationModel] = annotation_service.get_dict()
        annotations_container = AnnotationTreeItems(annotations=annotations)
        file_utils.write(file_path, annotations_container.json(indent=2))

    slide_name = QFileInfo(QFile(slide_path)).baseName()
    default_file_name = f"{slide_name}_annotations"
    select_image_file_action = SelectJsonFileAction("internal", None, on_select_file, default_file_name)
    select_image_file_action.trigger()
