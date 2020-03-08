from typing import List

import openslide
from shapely.geometry import Polygon, MultiPolygon
from shapely.strtree import STRtree

from common_image.core.img_polygon_utils import create_polygon_image, draw_source_on_target_polygon
from common_image.core.object_convert import pilimg_to_ndimg
from common_image.core.resize import resize_ndimg
from common_image.model.ndimg import Ndimg
from common_shapely.shapely_utils import locate, scale_at_origin, get_polygon_bbox_pos, get_polygon_bbox_size
from slide_viewer.ui.odict.deep.model import AnnotationModel


def get_slide_polygon_bbox_rgb_region(slide: openslide.AbstractSlide, polygon0: Polygon, level: int,
                                      target_color_mode='RGB', rescale_result_image=True) -> Ndimg:
    """
    :param polygon0: polygon with 0level coordinates
    :return: image_region with size = polygon_bbox_size if rescale_result_image=True else polygon_bbox_size / level_scale
    """
    pos = get_polygon_bbox_pos(polygon0)
    level = min(level, slide.level_count - 1)
    level_scale = 1 / slide.level_downsamples[level]
    nrows, ncols = get_polygon_bbox_size(polygon0, level_scale)
    pilimg = slide.read_region(pos, level, (ncols, nrows))
    pilimg = pilimg.convert(target_color_mode)
    if rescale_result_image:
        height, width = get_polygon_bbox_size(polygon0)
        if pilimg.size != (width, height):
            pilimg = pilimg.resize((width, height))
    # TODO consider borders, mirroring if region intersects border of slide
    ndimg = pilimg_to_ndimg(pilimg)
    return ndimg


def create_annotation_polygon_image(slide: openslide.AbstractSlide,
                                    annotation: AnnotationModel, annotation_geom: Polygon, polygon0: Polygon,
                                    zlayers_rtrees: List[STRtree], rescale_result_image=True) -> Ndimg:
    filter_level = annotation.filter_level if annotation.filter_level is not None else min(2, slide.level_count - 1)
    filter_level = int(filter_level)

    level_scale = 1 / slide.level_downsamples[filter_level]

    # TODO mask color - is filter too!?
    mask_color = annotation.user_attrs.get('label_color')
    if mask_color is not None:
        polygon_ = scale_at_origin(locate(polygon0, polygon0), level_scale)
        polygon_image = create_polygon_image(polygon_, 'L', mask_color)
        if rescale_result_image:
            nrows, ncols = get_polygon_bbox_size(polygon0)
            if polygon_image.ndarray.shape[:2] != (nrows, ncols):
                polygon_image = resize_ndimg(polygon_image, (nrows, ncols))

        return polygon_image


def create_layer_polygon_image(slide: openslide.AbstractSlide, polygon0: Polygon, level: int,
                               zlayers_rtrees: List[STRtree], target_color_mode='RGB', rescale_result_image=True) -> Ndimg:
    """
      :param polygon0: polygon with 0level coordinates
      :return: image from top layer with size = polygon_bbox_size if rescale_result_image=True else polygon_bbox_size / level_scale
    """
    if not zlayers_rtrees:
        return get_slide_polygon_bbox_rgb_region(slide, polygon0, level,
                                                 target_color_mode=target_color_mode, rescale_result_image=rescale_result_image)

    # We search intersections only for last(top most) z-index layer.
    # We do not search intersections for all layers to detect if polygon is fully labeled or is inside ROI.
    # It means all filtering of not relevant patches must be performed outside.
    probable_intersecting_geoms0 = zlayers_rtrees[-1].query(polygon0)
    intersecting_geoms0 = [geom for geom in probable_intersecting_geoms0 if geom.intersects(polygon0)]
    intersecting_geoms_intersections0 = [geom.intersection(polygon0) for geom in intersecting_geoms0]
    intersection_area = sum([i.area for i in intersecting_geoms_intersections0])

    level = min(level, slide.level_count - 1)
    level_scale = 1 / slide.level_downsamples[level]
    if intersection_area != polygon0.area:
        below_layer_polygon_img = create_layer_polygon_image(slide, polygon0, level, zlayers_rtrees[:-1], target_color_mode, rescale_result_image)
        polygon_img = below_layer_polygon_img
    elif not rescale_result_image:
        polygon = scale_at_origin(polygon0, level_scale)
        polygon_img = create_polygon_image(polygon, target_color_mode)
    else:
        polygon_img = create_polygon_image(polygon0, target_color_mode)

    for intersecting_geom0, intersecting_geom_intersection0 in zip(intersecting_geoms0, intersecting_geoms_intersections0):
        if isinstance(intersecting_geom_intersection0, Polygon):
            intersecting_geoms_polygons0 = [intersecting_geom_intersection0]
        elif isinstance(intersecting_geom_intersection0, MultiPolygon):
            intersecting_geoms_polygons0 = intersecting_geom_intersection0.geoms
        else:
            print(f"Ignoring not Polygon intersection {intersecting_geom_intersection0}")
            continue
        for intersecting_geom_polygon0 in intersecting_geoms_polygons0:
            if not rescale_result_image:
                intersecting_geom_polygon = scale_at_origin(locate(intersecting_geom_polygon0, polygon0), level_scale)
            else:
                intersecting_geom_polygon = locate(intersecting_geom_polygon0, polygon0)
            annotation_polygon_image = create_annotation_polygon_image(slide, intersecting_geom0.annotation, intersecting_geom0,
                                                                       intersecting_geom_polygon, zlayers_rtrees[:-1], rescale_result_image)
            draw_source_on_target_polygon(polygon_img, intersecting_geom_polygon, annotation_polygon_image)

    return polygon_img
