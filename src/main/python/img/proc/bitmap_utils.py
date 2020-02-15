from PyQt5.QtCore import Qt
from PyQt5.QtGui import QBitmap, QPolygon, QPainter, QPen, QBrush

from img.pos import ituple
from img.proc.region import RegionData, deshift_points, rescale_points
from slide_viewer.cache_config import gcached
from common_qt.qobjects_convert_util import ituple_to_qsize, ituple_to_qpoint, ituples_to_qpoints
from slide_viewer.ui.model.annotation_type import AnnotationType


@gcached
def region_data_to_bitmap(rd: RegionData, pixmap_size: ituple) -> QBitmap:
    bitmap = QBitmap(ituple_to_qsize(pixmap_size))
    level0_qsize = QPolygon([ituple_to_qpoint(p) for p in rd.points]).boundingRect().size()
    sx, sy = bitmap.width() / level0_qsize.width(), bitmap.height() / level0_qsize.height()
    points = deshift_points(rd.points, rd.origin_point)
    points = rescale_points(points, sx, sy)
    # bounding_rect = QPolygon(ituples_to_qpoints(points)).boundingRect()
    painter = QPainter(bitmap)
    pen = QPen(Qt.color0)
    brush = QBrush(Qt.color0)
    painter.setPen(pen)
    painter.setBrush(brush)
    painter.drawRect(bitmap.rect())
    brush.setColor(Qt.color1)
    pen.setColor(Qt.color1)
    painter.setPen(pen)
    painter.setBrush(brush)
    if rd.annotation_type is AnnotationType.RECT:
        painter.drawRect(bitmap.rect())
    elif rd.annotation_type is AnnotationType.ELLIPSE:
        painter.drawEllipse(bitmap.rect())
    elif rd.annotation_type is AnnotationType.POLYGON:
        qpoints = ituples_to_qpoints(points)
        painter.drawPolygon(QPolygon(qpoints))
    elif rd.annotation_type is AnnotationType.LINE:
        pen.setWidth(50)
        p1, p2 = ituples_to_qpoints(points)
        painter.drawLine(p1, p2)
    painter.end()
    return bitmap