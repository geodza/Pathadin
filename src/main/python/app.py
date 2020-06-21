import sys
import warnings

from PIL import Image
from PyQt5 import QtCore
from PyQt5.QtGui import *

from common_qt.util.message_handler import qt_message_handler
from slide_viewer.app_context import AppContext
from slide_viewer.config import cache_size_in_kb


if __name__ == '__main__':
	appctxt = AppContext()
	warnings.simplefilter('error', Image.DecompressionBombWarning)
	QtCore.qInstallMessageHandler(qt_message_handler)
	QPixmapCache.setCacheLimit(cache_size_in_kb)
	exit_code = appctxt.run()
	sys.exit(exit_code)
