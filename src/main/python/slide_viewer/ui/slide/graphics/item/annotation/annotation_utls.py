from PyQt5.QtCore import QMarginsF
from PyQt5.QtGui import QPen, QColor
from PyQt5.QtWidgets import QApplication


def create_annotation_pen(color=QColor(0, 230, 255), width=2):
    pen = QPen(color, width)
    pen.setCosmetic(True)
    return pen


def create_annotation_text_font():
    f = QApplication.font()
    f.setPointSize(int(f.pointSize() * 1.2))
    return f


def create_annotation_text_brush():
    return QColor(0, 230, 255)


def create_annotation_text_margins():
    return QMarginsF(4, 4, 4, 4)
