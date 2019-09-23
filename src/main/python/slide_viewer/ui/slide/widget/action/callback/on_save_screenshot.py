from datetime import datetime

from PyQt5.QtCore import QFileInfo, QFile, QPoint

from slide_viewer.ui.common.select_image_file_action import SelectImageFileAction
from slide_viewer.ui.common.screenshot_builders import build_screenshot_image_from_view
from slide_viewer.ui.slide.widget.slide_viewer_widget import SlideViewerWidget


def on_save_screenshot(widget: SlideViewerWidget):
    def on_select_image_file(image_file: str):
        image = build_screenshot_image_from_view(widget.view)
        image.save(image_file)

    if widget.slide_helper:
        now = datetime.now()
        now_str = now.strftime("%d-%m-%Y_%H-%M-%S")
        slide_name = QFileInfo(QFile(widget.slide_helper.slide_path)).baseName()
        default_file_name = f"{slide_name}_screen_{now_str}"
        select_image_file_action = SelectImageFileAction("internal", widget, on_select_image_file,
                                                         default_file_name)
        select_image_file_action.trigger()
