from typing import Iterable, List

from PyQt5.QtCore import QPointF, QPoint, QSizeF, QSize

from img.pos import ituple, ftuple


def qpointf_to_ftuple(p: QPointF) -> ftuple:
    return (p.x(), p.y())


def qpoint_to_ituple(p: QPoint) -> ituple:
    return (p.x(), p.y())


def qpointfs_to_ftuples(points: Iterable[QPointF]) -> List[ftuple]:
    return list(map(qpointf_to_ftuple, points))


def qpoints_to_ituples(points: Iterable[QPoint]) -> List[ituple]:
    return list(map(qpoint_to_ituple, points))


def ftuple_to_qpointf(p: ftuple) -> QPointF:
    return QPointF(*p)


def ituple_to_qpoint(p: ituple) -> QPoint:
    return QPoint(*p)


def ftuple_to_ituple(p: ftuple) -> ituple:
    return (int(p[0]), int(p[1]))


def ftuples_to_ituples(points: Iterable[ftuple]) -> List[ituple]:
    return list(map(ftuple_to_ituple, points))


def ituples_to_qpoints(points: Iterable[ituple]) -> List[QPoint]:
    return list(map(ituple_to_qpoint, points))


def ftuples_to_qpointfs(points: Iterable[ftuple]) -> List[QPoint]:
    return list(map(ituple_to_qpoint, points))


def qsizef_to_ftuple(size: QSizeF) -> ftuple:
    return (size.width(), size.height())


def qsize_to_ituple(size: QSize) -> ituple:
    return (size.width(), size.height())


def ituple_to_qsize(size: ituple) -> QSize:
    return QSize(*size)


def ftuple_to_qsizef(size: ftuple) -> QSizeF:
    return QSizeF(*size)
