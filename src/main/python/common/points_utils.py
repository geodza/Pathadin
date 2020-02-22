from typing import Iterable, Tuple

ituple = Tuple[int, int]
ituples = Tuple[ituple, ...]


def deshift_points(points: Iterable[ituple], origin_point: ituple) -> Iterable[ituple]:
    origin_point_deshifted = [(p[0] - origin_point[0], p[1] - origin_point[1]) for p in points]
    left = min(origin_point_deshifted, key=lambda p: p[0])
    top = min(origin_point_deshifted, key=lambda p: p[1])
    new_origin_point = (left[0], top[1])
    first_point_shifted = [(p[0] - new_origin_point[0], p[1] - new_origin_point[1]) for p in origin_point_deshifted]
    return tuple(first_point_shifted)


def rescale_points(points: Iterable[ituple], sx: float, sy: float) -> Iterable[ituple]:
    rescaled_points = [(int(p[0] * sx), int(p[1] * sy)) for p in points]
    return tuple(rescaled_points)
