import sys

from PyQt5.QtGui import *
from PyQt5.QtWidgets import QApplication

from slide_viewer.config import cache_size_in_kb, main_window_start_size
from slide_viewer.slide_viewer_main_window import SlideViewerMainWindow


def excepthook(excType, excValue, tracebackobj):
    print(excType, excValue, tracebackobj)


sys.excepthook = excepthook

if __name__ == "__main__":
    app = QApplication(sys.argv)
    QPixmapCache.setCacheLimit(cache_size_in_kb)

    win = SlideViewerMainWindow()
    win.resize(*main_window_start_size)
    win.show()

    sys.exit(app.exec_())
