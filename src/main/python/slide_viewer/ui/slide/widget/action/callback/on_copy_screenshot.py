from PyQt5.QtGui import QGuiApplication, QCursor
from PyQt5.QtWidgets import QAction, QToolTip

from slide_viewer.ui.common.screenshot_builders import build_screenshot_image_from_view
from slide_viewer.ui.slide.graphics.slide_viewer_graphics_view import SlideViewerGraphicsView


def on_copy_screenshot(view: SlideViewerGraphicsView):
    image = build_screenshot_image_from_view(view)
    QGuiApplication.clipboard().setImage(image)
    QToolTip.showText(QCursor.pos(), "Screenshot copied to clipboard!")
