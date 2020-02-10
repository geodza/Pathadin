from datetime import datetime

from PyQt5.QtCore import QFileInfo, QFile

from slide_viewer.ui.common.action.select_image_file_action import SelectImageFileAction
from slide_viewer.common_qt.screenshot_builders import build_screenshot_image_from_view
from slide_viewer.ui.slide.graphics.view.graphics_view import GraphicsView


def on_save_screenshot(view: GraphicsView) -> None:
    def on_select_image_file(image_file: str) -> None:
        image = build_screenshot_image_from_view(view)
        image.save(image_file)

    if view.slide_helper:
        now = datetime.now()
        now_str = now.strftime("%d-%m-%Y_%H-%M-%S")
        slide_name = QFileInfo(QFile(view.slide_helper.slide_path)).baseName()
        default_file_name = f"{slide_name}_screen_{now_str}"
        select_image_file_action = SelectImageFileAction("internal", view, on_select_image_file,
                                                         default_file_name)
        select_image_file_action.trigger()
