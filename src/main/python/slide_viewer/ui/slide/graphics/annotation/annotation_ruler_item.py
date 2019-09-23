from PyQt5.QtCore import QRectF, QSizeF, QPointF, QRect, Qt, QMutex, QMutexLocker, QPoint, QLine, QLineF, QMargins, \
    QMarginsF
from PyQt5.QtGui import *
from PyQt5.QtWidgets import QGraphicsItem, QWidget, QStyleOptionGraphicsItem, QGraphicsTextItem, QGraphicsItemGroup, \
    QGraphicsScene, QGraphicsLineItem, QGraphicsSimpleTextItem, QGraphicsRectItem


class AnnotationRulerItem(QGraphicsItemGroup):
    def __init__(self, p1: QPointF = QPointF(), p2: QPointF = QPointF()):
        super().__init__()

        self.line = QGraphicsLineItem()
        pen = QPen(QColor(0, 230, 255), 2)
        pen.setCosmetic(True)
        self.line.setPen(pen)
        self.addToGroup(self.line)

        self.text_background = QGraphicsRectItem()
        self.text_background.setBrush(QColor(0, 230, 255))
        self.text_background.setFlag(QGraphicsItem.ItemIgnoresTransformations, True)
        self.addToGroup(self.text_background)

        self.text = QGraphicsSimpleTextItem()
        self.text.setAcceptHoverEvents(False)
        self.text.setFlag(QGraphicsItem.ItemIgnoresTransformations, True)
        f = self.text.font()
        f.setPointSize(int(f.pointSize() * 1.2))
        self.text.setFont(f)
        self.addToGroup(self.text)

        self.update(p1, p2)
        # self.setFlag(QGraphicsItem.ItemIgnoresTransformations, True)

        # self.line.setFlag(QGraphicsItem.ItemIgnoresTransformations, True)
        # self.text.setScale(5)
        # self.setFlag(QGraphicsItem.ItemClipsToShape, True)
        # self.setFlag(QGraphicsItem.ItemClipsChildrenToShape, True)
        # self.setAcceptedMouseButtons(Qt.NoButton)
        # self.setAcceptHoverEvents(False)

    def update(self, p1: QPointF, p2: QPointF):
        # self.line.setPoints(self.mapFromScene(p1), self.mapFromScene(p2))
        self.line.setLine(QLineF(p1, p2))
        x1, y1 = self.line.line().p1().x(), self.line.line().p1().y()
        x2, y2 = self.line.line().p2().x(), self.line.line().p2().y()
        length = ((x1 - x2) ** 2 + (y1 - y2) ** 2) ** 0.5
        self.text.setText(str(length))
        text_background_margins = QMarginsF(4, 4, 4, 4)
        self.text_background.setRect(self.text.boundingRect() + text_background_margins)
        self.text.setPos(self.line.line().center())
        self.text_background.setPos(self.line.line().center())
