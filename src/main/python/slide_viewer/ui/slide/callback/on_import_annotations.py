from PyQt5.QtCore import QFileInfo, QFile

from slide_viewer.ui.common.action.select_json_file_action import SelectJsonFileAction
from slide_viewer.ui.odict.deep.deepable_tree_view import DeepableTreeView
from slide_viewer.ui.odict.deep.model import AnnotationTreeItems
from slide_viewer.ui.slide.widget.interface.slide_path_provider import SlidePathProvider


def load_annotations(view: DeepableTreeView, file_path: str) -> None:
    annotations_container = AnnotationTreeItems.parse_file(file_path)
    if annotations_container and annotations_container.annotations:
        view.model().clear()
        # view.scene().clear_annotations()
        for key, value in annotations_container.annotations.items():
            view.model()[key] = value
            # view.scene().add_annotation(value)


def on_import_annotations(view: DeepableTreeView, slide_path:str) -> None:
    slide_name = QFileInfo(QFile(slide_path)).baseName()
    default_file_name = f"{slide_name}_annotations.json"

    def f(file_path: str) -> None:
        load_annotations(view, file_path)

    select_image_file_action = SelectJsonFileAction("internal", view, f, default_file_name, False)
    select_image_file_action.trigger()
