import sys

from PyQt5.QtGui import *

from slide_viewer.config import cache_size_in_kb
from slide_viewer.ui.slide.widget.slide_viewer_app_context import AppContext


def excepthook(excType, excValue, tracebackobj):
    print(excType, excValue, tracebackobj)


sys.excepthook = excepthook

if __name__ == '__main__':
    appctxt = AppContext()
    QPixmapCache.setCacheLimit(cache_size_in_kb)
    exit_code = appctxt.run()
    sys.exit(exit_code)
