from typing import List

from shapely.affinity import translate
from shapely.geometry import Polygon
from shapely.geometry.base import BaseGeometry

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
    else:
        # ignore ellipse and line
        print(f"Ignoring not polygon or rect geometry: {geometry}")
        pass


def annotation_to_geom(annotation: AnnotationModel, prepare=False) -> BaseGeometry:
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


def load_annotation_geoms(annotations_path: str) -> List[BaseGeometry]:
    annotations_container = AnnotationTreeItems.parse_file(annotations_path)
    annotations = annotations_container.annotations

    train_annotations = [a for a in annotations.values() if a.label != 'test']

    annotation_geoms = [annotation_to_geom(a, True) for a in train_annotations]
    return annotation_geoms