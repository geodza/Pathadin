from PyQt5.QtGui import QGuiApplication, QCursor
from PyQt5.QtWidgets import QToolTip

from slide_viewer.common_qt.screenshot_builders import build_screenshot_image_from_view
from slide_viewer.ui.slide.graphics.graphics_view import GraphicsView


def on_copy_screenshot(view: GraphicsView) -> None:
    image = build_screenshot_image_from_view(view)
    # image = build_screenshot_image_from_scene(view.scene(), view.mapToScene(view.viewport().rect()).boundingRect())
    QGuiApplication.clipboard().setImage(image)
    QToolTip.showText(QCursor.pos(), "Screenshot copied to clipboard!")
