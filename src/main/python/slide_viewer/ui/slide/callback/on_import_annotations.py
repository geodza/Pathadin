from PyQt5.QtCore import QFileInfo, QFile

from common_qt.select_json_file_action import SelectJsonFileAction
from slide_viewer.ui.odict.deep.model import AnnotationTreeItems
from slide_viewer.ui.slide.widget.interface.annotation_service import AnnotationService


def load_annotations(annotation_service: AnnotationService, file_path: str) -> None:
    annotations_container = AnnotationTreeItems.parse_file(file_path)
    if annotations_container and annotations_container.annotations:
        annotation_service.delete_all()
        # view.scene().clear_annotations()
        for key, value in annotations_container.annotations.items():
            annotation_service.add_or_edit(key, value)


def on_import_annotations(annotation_service: AnnotationService, slide_path: str) -> None:
    slide_name = QFileInfo(QFile(slide_path)).baseName()
    default_file_name = f"{slide_name}_annotations.json"

    def f(file_path: str) -> None:
        load_annotations(annotation_service, file_path)

    select_image_file_action = SelectJsonFileAction("internal", None, f, default_file_name, False)
    select_image_file_action.trigger()
