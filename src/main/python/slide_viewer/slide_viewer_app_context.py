from PyQt5.QtGui import QImage
from fbs_runtime.application_context import cached_property
from fbs_runtime.application_context.PyQt5 import ApplicationContext

from slide_viewer.config import initial_main_window_size
from slide_viewer.slide_viewer_main_window import SlideViewerMainWindow


class AppContext(ApplicationContext):

    def __init__(self, *args, **kwargs):
        super(AppContext, self).__init__(*args, **kwargs)
        self.slide_viewer_main_window = SlideViewerMainWindow(self)

    def run(self):
        # self.slide_viewer_main_window.resize(*initial_main_window_size)
        self.slide_viewer_main_window.show()
        self.slide_viewer_main_window.on_select_slide_file_action(self.get_resource("initial_image.jpg"))
        # self.slide_viewer_main_window.on_select_slide_file_action(slide_path)
        return self.app.exec_()

    @cached_property
    def icon_magnifier(self):
        return QImage(self.get_resource('magnifier.ico'))

    @cached_property
    def icon_grid(self):
        return QImage(self.get_resource('grid.ico'))

    @cached_property
    def icon_fit(self):
        return QImage(self.get_resource('fit.ico'))
