from collections import defaultdict
from typing import List

from shapely.affinity import translate
from shapely.geometry import Polygon
from shapely.geometry.base import BaseGeometry
from shapely.strtree import STRtree

from slide_viewer.ui.model.annotation_type import AnnotationType
from slide_viewer.ui.odict.deep.model import AnnotationModel, AnnotationTreeItems
from slide_viewer.ui.slide.graphics.item.annotation.model import AnnotationGeometry


def annotation_geom_to_shapely_geom(geometry: AnnotationGeometry) -> BaseGeometry:
    shift = geometry.origin_point or (0, 0)
    if geometry.annotation_type == AnnotationType.POLYGON:
        return translate(Polygon(geometry.points), *shift)
    elif geometry.annotation_type == AnnotationType.RECT:
        p1, p2 = geometry.points
        # return box(p1[0], p1[1], p2[0], p2[1])
        return translate(Polygon([p1, (p2[0], p1[1]), p2, (p1[0], p2[1]), p1]), *shift)
    # TODO another types
    else:
        # ignore ellipse and line
        print(f"Ignoring not polygon or rect geometry: {geometry}")
        pass


def annotation_to_geom(annotation: AnnotationModel, prepare=False) -> BaseGeometry:
    geom = annotation_geom_to_shapely_geom(annotation.geometry)
    if geom:
        if not geom.is_valid:
            geom = geom.buffer(0)
        if not geom.is_valid:
            print(f'invalid geom: {annotation}')
        # if prepare:
        #     geom = prep(geom)
        geom.annotation = annotation
        return geom
    return None


def create_zlayers_rtrees(annotation_geoms: List[BaseGeometry]) -> List[STRtree]:
    z_to_geoms = defaultdict(list)
    for geom in annotation_geoms:
        z = geom.annotation.user_attrs.get('z_index', 0)
        z_to_geoms[z].append(geom)

    z_list = sorted(z_to_geoms.keys())
    zlayers_rtrees = list([STRtree(z_to_geoms[z]) for z in z_list])
    return zlayers_rtrees


def load_annotation_geoms(annotations_path: str) -> List[BaseGeometry]:
    annotations_container = AnnotationTreeItems.parse_file(annotations_path)
    annotations = annotations_container.annotations
    annotation_geoms = [annotation_to_geom(a, True) for a in annotations.values()]
    not_none_annotation_geoms = [a for a in annotation_geoms if a]
    return not_none_annotation_geoms
