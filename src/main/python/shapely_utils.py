from collections import OrderedDict
from math import ceil
from typing import List, Tuple, Callable

from dataclasses import dataclass
from shapely.affinity import translate, scale
from shapely.geometry import Polygon, box
from shapely.geometry.base import BaseGeometry
from shapely.ops import unary_union
from shapely.prepared import prep
from shapely.strtree import STRtree

from common.grid_utils import pos_range, pos_to_rect_coords
from slide_viewer.ui.model.annotation_type import AnnotationType
from slide_viewer.ui.odict.deep.model import AnnotationModel
from slide_viewer.ui.slide.graphics.item.annotation.model import AnnotationGeometry

def annotation_geom_to_shapely_geom(geometry: AnnotationGeometry) -> BaseGeometry:
    shift = geometry.origin_point or (0, 0)
    if geometry.annotation_type == AnnotationType.POLYGON:
        return translate(Polygon(geometry.points), *shift)
    elif geometry.annotation_type == AnnotationType.RECT:
        p1, p2 = geometry.points
        # return box(p1[0], p1[1], p2[0], p2[1])
        return translate(Polygon([p1, (p2[0], p1[1]), p2, (p1[0], p2[1]), p1]), *shift)
    else:
        # ignore ellipse and line
        print(f"Ignoring not polygon or rect geometry: {geometry}")
        pass


def annotation_to_geom(annotation: AnnotationModel, prepare=False):
    geom = annotation_geom_to_shapely_geom(annotation.geometry)
    if geom:
        if not geom.is_valid:
            print(f'invalid geom: {annotation}')
        geom = geom if geom.is_valid else geom.buffer(0)
        # if prepare:
        #     geom = prep(geom)
        geom.annotation = annotation
        return geom
    return None


def build_annotations_union_and_rtree(annotations: List[AnnotationModel]):
    geoms = []
    for a in annotations:
        id_ = a.id
        geom = annotation_geom_to_shapely_geom(a.geometry)
        if geom:
            if not geom.is_valid:
                print(f'invalid geom: {id_}')
            geom = geom if geom.is_valid else geom.buffer(0)
            geom.annotation_id = id_
            geoms.append(geom)
    geoms_union = unary_union(geoms)
    rtree = STRtree(geoms)
    return geoms_union, rtree


def build_pos_to_annotation_polygons(annotations: List[AnnotationModel],
                                     source_size: Tuple[int, int], grid_length: int):
    annotations_union_, rtree = build_annotations_union_and_rtree(annotations)
    union_xmin, union_ymin, union_xmax, union_ymax = annotations_union_.bounds
    annotations_union = prep(annotations_union_)
    # tile_box = LinearRing()
    pos_to_annotation_polygons = OrderedDict()
    for pos in pos_range(source_size, grid_length):
        # tile_box = box(pos[0], pos[1], pos[0] + grid_length, pos[1] + grid_length)
        # Shapely uses upward y-axis and Qt uses downward y-axis, be careful with this discrepancy
        xmin, ymin, xmax, ymax = pos_to_rect_coords(pos, grid_length)
        if xmin <= union_xmax and xmax >= union_xmin and ymin <= union_ymax and ymax >= union_ymin:
            tile_box = box(*pos_to_rect_coords(pos, grid_length))
            # tile_box.coords = [pos, (pos[0] + grid_length, pos[1]), (pos[0] + grid_length, pos[1] + grid_length),
            #                    (pos[0], pos[1] + grid_length), pos]
            intersections = rtree.query(tile_box)
            if intersections and annotations_union.contains(tile_box):
                pos_to_annotation_polygons[pos] = [i for i in intersections if tile_box.intersects(i)]
    return pos_to_annotation_polygons


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


# def contains2(source:BaseGeometry, ):
#     xmin, ymin, xmax, ymax = pos_to_rect_coords(pos, grid_length)
#     if xmin <= union_xmax and xmax >= union_xmin and ymin <= union_ymax and ymax >= union_ymin:
#     source.bounds
#     source.contains(target)

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
