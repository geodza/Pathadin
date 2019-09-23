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
