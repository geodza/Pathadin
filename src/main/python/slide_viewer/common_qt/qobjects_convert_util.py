from typing import Iterable, Tuple, List

from PyQt5.QtCore import QPointF, QPoint

ituple = Tuple[int, int]
ituples = Tuple[ituple, ...]
ftuple = Tuple[float, float]


def qpointf_to_tuple(p: QPointF) -> ftuple:
    return (p.x(), p.y())


def qpoint_to_tuple(p: QPoint) -> ituple:
    return (p.x(), p.y())


def qpointfs_to_tuples(points: Iterable[QPointF]) -> List[ftuple]:
    return list(map(qpointf_to_tuple, points))


def qpoints_to_tuples(points: Iterable[QPoint]) -> List[ituple]:
    return list(map(qpoint_to_tuple, points))


def tuple_to_qpointf(p: ftuple) -> QPointF:
    return QPointF(*p)


def tuple_to_qpoint(p: ituple) -> QPoint:
    return QPoint(*p)


def tuples_to_qpoints(points: Iterable[ituple]) -> List[QPoint]:
    return list(map(tuple_to_qpoint, points))


def tuples_to_qpointfs(points: Iterable[ftuple]) -> List[QPoint]:
    return list(map(tuple_to_qpoint, points))
