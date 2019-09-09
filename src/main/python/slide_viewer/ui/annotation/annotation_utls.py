from collections import OrderedDict

from PyQt5.QtCore import QMarginsF, QPointF
from PyQt5.QtGui import QPen, QColor
from PyQt5.QtWidgets import QApplication, QGraphicsItemGroup

from slide_viewer.ui.annotation.annotation_data import AnnotationData
from slide_viewer.ui.annotation.annotation_type import AnnotationType
from slide_viewer.ui.dict_tree_view_model.ordered_dicts_tree_model import StandardAttrKey


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


def create_item(dict_: dict):
    pass


def point_to_tuple(p: QPointF):
    return (p.x(), p.y())


def tuple_to_point(p: tuple):
    return QPointF(*p)


def update_ordered_dict_by_data(data: AnnotationData, odict: OrderedDict):
    odict[StandardAttrKey.name.name] = data.name
    odict[StandardAttrKey.points.name] = tuple(map(point_to_tuple, data.points))
    odict[StandardAttrKey.pen_color.name] = data.pen_color.name()
    odict[StandardAttrKey.text_background_color.name] = data.text_background_color.name()
    odict[StandardAttrKey.annotation_type.name] = data.annotation_type.name


def update_data_by_ordered_dict(data: AnnotationData, odict: OrderedDict):
    data.name = odict[StandardAttrKey.name.name]
    data.points = tuple(map(tuple_to_point, odict[StandardAttrKey.points.name]))
    data.pen_color = QColor(odict[StandardAttrKey.pen_color.name])
    data.text_background_color = QColor(odict[StandardAttrKey.text_background_color.name])
    data.annotation_type = AnnotationType[odict[StandardAttrKey.annotation_type.name]]


def ordered_dict_to_data(odict: OrderedDict):
    data = AnnotationData()
    update_data_by_ordered_dict(data, odict)
    return data


def update_item_by_data(annotation_item: QGraphicsItemGroup, data: AnnotationData):
    annotation_item.set_data(data)
    return
    annotation_item.set_points(data.points)

    pen = annotation_item.shape_item.pen()
    pen.setColor(data.pen_color)
    annotation_item.shape_item.setPen(pen)

    annotation_item.annotation_text.text.setText(data.name)
    brush = annotation_item.annotation_text.background.brush()
    brush.setColor(data.text_background_color)
    annotation_item.annotation_text.background.setBrush(brush)


def update_data_by_item(annotation_item: QGraphicsItemGroup, data: AnnotationData):
    pass
    # data.points = annotation_item.get_points()
    # data.name = annotation_item.annotation_text.text.text()
    # data.pen_color = annotation_item.shape_item.pen().color()
    # data.text_background_color = annotation_item.annotation_text.background.brush().color()
