from PyQt5.QtGui import QImage, QIcon
from fbs_runtime.application_context import cached_property
from fbs_runtime.application_context.PyQt5 import ApplicationContext

from slide_viewer.config import initial_main_window_size, slide_path
from slide_viewer.slide_viewer_main_window import SlideViewerMainWindow


class AppContext(ApplicationContext):

    def __init__(self, *args, **kwargs):
        super(AppContext, self).__init__(*args, **kwargs)
        self.slide_viewer_main_window = SlideViewerMainWindow(self)

    def run(self):
        # self.slide_viewer_main_window.resize(*initial_main_window_size)
        self.slide_viewer_main_window.show()
        # self.slide_viewer_main_window.on_select_slide_file_action(self.get_resource("initial_image.jpg"))
        self.slide_viewer_main_window.on_select_slide_file_action(slide_path)
        return self.app.exec_()

    @cached_property
    def icon_open(self):
        return QIcon(self.get_resource('folder_open.svg'))

    @cached_property
    def icon_magnifier(self):
        return QIcon(self.get_resource('search.svg'))

    @cached_property
    def icon_grid(self):
        return QIcon(self.get_resource('grid_on.svg'))

    @cached_property
    def icon_fit(self):
        return QIcon(self.get_resource('zoom_out_map.svg'))

    @cached_property
    def icon_screenshot(self):
        return QIcon(self.get_resource('photo_camera.svg'))

    @cached_property
    def icon_palette(self):
        return QIcon(self.get_resource('color_lens.svg'))

    @cached_property
    def icon_description(self):
        return QIcon(self.get_resource('description.svg'))
