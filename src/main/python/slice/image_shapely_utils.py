from typing import List

import openslide
from dataclasses import asdict
from shapely.geometry import Polygon
from shapely.strtree import STRtree

from common.dict_utils import remove_none_values
from common_image.core.mode_convert import convert_ndimg
from common_image.core.object_convert import pilimg_to_ndimg
from common_image.core.img_polygon_utils import create_polygon_image, get_polygon_bbox_image_view, draw_source_on_target_polygon
from common_image.model.ndimg import Ndimg
from common_shapely.shapely_utils import locate, scale_at_origin, get_polygon_bbox_pos, get_polygon_bbox_size
from img.filter.base_filter import FilterData, FilterType
from img.filter.kmeans_filter import KMeansFilterData
from img.filter.skimage_threshold import SkimageThresholdParams, SkimageThresholdType
from common_image.core.skimage_threshold import  ndimg_to_skimage_thresholded_ndimg
from slide_viewer.ui.odict.deep.model import AnnotationModel


def get_slide_polygon_bbox_rgb_region(slide: openslide.AbstractSlide, polygon: Polygon, level: int) -> Ndimg:
    """
    :param polygon: polygon with 0level coordinates
    :return: polygon bbox slide region downsized by level scale with color mode 'RGBA'
    """
    pos = get_polygon_bbox_pos(polygon)
    level_scale = 1 / slide.level_downsamples[level]
    nrows, ncols = get_polygon_bbox_size(polygon, level_scale)
    pilimg = slide.read_region(pos, level, (ncols, nrows))
    pilimg = pilimg.convert('RGB')
    # TODO consider borders, mirroring if region intersects border of slide
    ndimg = pilimg_to_ndimg(pilimg)
    return ndimg


def get_filter(id: str) -> FilterData:
    return None


def process_filter(img: Ndimg, filter_data: FilterData) -> Ndimg:
    converted_ndimgdata = convert_ndimg(img, 'L')
    params = SkimageThresholdParams(SkimageThresholdType.threshold_mean, {})
    kwargs = remove_none_values(asdict(params.params))
    return ndimg_to_skimage_thresholded_ndimg(img.ndarray, params.type.name, **kwargs)
    # threshold_range = ndimg_to_skimage_threshold_range(params, converted_ndimgdata)
    # return ndimg_to_thresholded_ndimg(converted_ndimgdata, threshold_range)


def create_annotation_polygon_image(slide: openslide.AbstractSlide,
                                    annotation: AnnotationModel, annotation_geom: Polygon, polygon: Polygon,
                                    zlayers_rtrees: List[STRtree]) -> Ndimg:
    # filter = get_filter(annotation.filter_id)
    # filter_level = annotation.filter_level
    filter = KMeansFilterData("123")
    filter_level = 2
    level_scale = 1 / slide.level_downsamples[filter_level]

    # TODO mask color - is filter too!?
    mask_color = annotation.user_attrs.get('label_color')
    if mask_color is not None:
        polygon_ = scale_at_origin(locate(polygon, polygon), level_scale)
        return create_polygon_image(polygon_, 'L', mask_color)

    if filter.filter_type in [FilterType.KMEANS]:
        source_polygon = annotation_geom
    else:
        source_polygon = polygon
    target_polygon = scale_at_origin(locate(polygon, source_polygon), level_scale)

    source = create_layer_polygon_image(slide, source_polygon, filter_level, zlayers_rtrees[:-1])
    target_ = process_filter(source, filter)
    target = get_polygon_bbox_image_view(target_.ndarray, target_polygon)
    return Ndimg(target, target_.color_mode, target_.bool_mask_ndarray)


def create_layer_polygon_image(slide: openslide.AbstractSlide, polygon: Polygon, level: int,
                               zlayers_rtrees: List[STRtree]) -> Ndimg:
    if not zlayers_rtrees:
        return get_slide_polygon_bbox_rgb_region(slide, polygon, level)

    # We search intersections only for last(top most) z-index layer.
    # We do not search intersections for all layers to detect if polygon is fully labeled or is inside ROI.
    # It means all filtering of not relevant patches must be performed outside.
    probable_intersecting_geoms = zlayers_rtrees[-1].query(polygon)
    intersecting_geoms = [geom for geom in probable_intersecting_geoms if geom.intersects(polygon)]
    intersecting_geoms_intersections = [geom.intersection(polygon) for geom in intersecting_geoms]
    intersection_area = sum([i.area for i in intersecting_geoms_intersections])

    level_scale = 1 / slide.level_downsamples[level]
    if intersection_area != polygon.area:
        below_layer_polygon_img = create_layer_polygon_image(slide, polygon, level, zlayers_rtrees[:-1])
        polygon_img = below_layer_polygon_img
    else:
        polygon_ = scale_at_origin(polygon, level_scale)
        polygon_img = create_polygon_image(polygon_, 'RGB')

    for intersecting_geom, intersecting_geom_intersection in zip(intersecting_geoms, intersecting_geoms_intersections):
        if not isinstance(intersecting_geom_intersection, Polygon):
            # TODO consider geometry collection containing polygon
            print(f"Ignoring not Polygon intersection {intersecting_geom_intersection}")
            continue
        intersecting_geom_intersection_ = scale_at_origin(locate(intersecting_geom_intersection, polygon), level_scale)
        annotation_polygon_image = create_annotation_polygon_image(slide, intersecting_geom.annotation, intersecting_geom,
                                                                   intersecting_geom_intersection_, zlayers_rtrees[:-1])
        draw_source_on_target_polygon(polygon_img, intersecting_geom_intersection_, annotation_polygon_image)

    return polygon_img
