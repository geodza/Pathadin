from PyQt5.QtGui import QColor

from slide_viewer.ui.annotation.annotation_path_item import AnnotationPathItem
from slide_viewer.ui.annotation.annotation_data import AnnotationData
from slide_viewer.ui.annotation.annotation_type import AnnotationType

annotation_number = 1


class AnnotatioDataFactory:
    annotation_last_number = 0

    @staticmethod
    def default_annotation_data(annotation_type):
        AnnotatioDataFactory.annotation_last_number += 1
        color = "#50ff50"
        return AnnotationData([], f"annotation{AnnotatioDataFactory.annotation_last_number}", QColor(color),
                              QColor(color),
                              annotation_type)


def create_annotation_item(type: AnnotationType):
    if type == AnnotationType.LINE:
        # return AnnotationLineItem()
        return AnnotationPathItem(AnnotatioDataFactory.default_annotation_data(AnnotationType.LINE))
    elif type == AnnotationType.RECT:
        # return AnnotationRectItem()
        return AnnotationPathItem(AnnotatioDataFactory.default_annotation_data(AnnotationType.RECT))
    elif type == AnnotationType.ELLIPSE:
        return AnnotationPathItem(AnnotatioDataFactory.default_annotation_data(AnnotationType.ELLIPSE))
    elif type == AnnotationType.POLYGON:
        return AnnotationPathItem(AnnotatioDataFactory.default_annotation_data(AnnotationType.POLYGON))
