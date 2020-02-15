from PyQt5.QtCore import Qt
from PyQt5.QtGui import QColor
from PyQt5.QtWidgets import QColorDialog


def get_user_custom_color_names():
    color_indices = get_user_custom_color_indices()
    colors = [QColorDialog.customColor(i) for i in color_indices]
    color_names = [color.name() for color in colors if color not in (Qt.white, Qt.black)]
    return color_names


def get_user_custom_color_indices():
    colors = [QColorDialog.customColor(i) for i in range(QColorDialog.customCount())]
    color_indices = [i for i, color in enumerate(colors) if color not in (Qt.white, Qt.black)]
    return color_indices


def get_next_user_custom_color_index():
    color_indices = set(get_user_custom_color_indices())
    for i in range(QColorDialog.customCount()):
        if i not in color_indices:
            return i
    return 0


def add_user_custom_color(color: QColor):
    next_custom_index = get_next_user_custom_color_index()
    QColorDialog.setCustomColor(next_custom_index, color)


def set_user_custom_colors(color_names: list):
    for i, color_name in enumerate(color_names):
        custom_color = QColor(color_name)
        QColorDialog.setCustomColor(i, custom_color)
