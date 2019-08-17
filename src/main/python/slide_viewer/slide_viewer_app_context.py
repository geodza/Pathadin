from fbs_runtime.application_context.PyQt5 import ApplicationContext

from slide_viewer.config import main_window_start_size
from slide_viewer.slide_viewer_main_window import SlideViewerMainWindow


class AppContext(ApplicationContext):

    def __init__(self, *args, **kwargs):
        super(AppContext, self).__init__(*args, **kwargs)
        self.slide_viewer_main_window = SlideViewerMainWindow()

    def run(self):
        self.slide_viewer_main_window.resize(*main_window_start_size)
        self.slide_viewer_main_window.show()
        self.slide_viewer_main_window.slide_viewer_widget.load(self.get_resource('initial_image.jpg'))
        return self.app.exec_()
