from PyQt5.QtCore import QSize, QRectF, Qt, QSizeF, QPointF, QRect, QPoint
from PyQt5.QtGui import QImage, QPainter
from PyQt5.QtWidgets import QGraphicsScene, QGraphicsItemGroup, QGraphicsView


def build_screenshot_image_from_view(view: QGraphicsView) -> QImage:
    pixmap = view.viewport().grab()
    image = QImage(pixmap.size(), QImage.Format_RGBA8888)
    painter = QPainter(image)
    painter.drawPixmap(image.rect(), pixmap)
    painter.end()
    return image


def build_screenshot_image_from_scene(scene: QGraphicsScene, rect: QRectF) -> QImage:
    image = QImage(rect.size().toSize(), QImage.Format_RGBA8888)
    painter = QPainter(image)
    scene.render(painter, QRectF(image.rect()), rect)
    painter.end()
    return image


def render_scene_rect(image: QImage, scene: QGraphicsScene, rect: QRectF) -> QImage:
    painter = QPainter(image)
    scene.render(painter, QRectF(image.rect()), rect)
    painter.end()
