from dataclasses import dataclass
from math import ceil
from typing import Tuple, Callable

from shapely.affinity import translate, scale
from shapely.geometry import Polygon
from shapely.geometry.base import BaseGeometry


def locate(polygon: Polygon, origin: Polygon) -> Polygon:
    polygon_located_at_origin = translate(polygon, -origin.bounds[0], -origin.bounds[1])
    return polygon_located_at_origin


def scale_at_origin(polygon: Polygon, s: float) -> Polygon:
    polygon_scaled_at_origin = scale(polygon, s, s, origin=(0, 0))
    return polygon_scaled_at_origin


def get_polygon_bbox_pos(polygon: Polygon) -> Tuple[int, int]:
    minx, miny, maxx, maxy = polygon.bounds
    pos = (int(minx), int(miny))
    return pos


def get_polygon_bbox_size(polygon: Polygon, s: float = 1) -> Tuple[int, int]:
    minx, miny, maxx, maxy = polygon.bounds
    nrows, ncols = ceil((maxy - miny) * s), ceil((maxx - minx) * s)
    return nrows, ncols


def update_coords(geom: BaseGeometry, minx, miny, maxx, maxy):
    geom.coords = [(minx, miny), (minx, maxy), (maxx, maxy), (maxx, miny), (minx, miny)]


@dataclass
class ProbablyContainsChecker:
    minx: float
    miny: float
    maxx: float
    maxy: float

    def probably_contains(self, minx: float, miny: float, maxx: float, maxy: float) -> bool:
        return minx <= self.maxx and maxx >= self.minx and miny <= self.maxy and maxy >= self.miny


def create_probably_contains_func(self_minx: float, self_miny: float, self_maxx: float, self_maxy: float) \
        -> Callable[[float, float, float, float], bool]:
    def probably_contains(minx: float, miny: float, maxx: float, maxy: float) -> bool:
        return minx <= self_maxx and maxx >= self_minx and miny <= self_maxy and maxy >= self_miny

    return probably_contains