import pathlib
from itertools import islice
from math import ceil
from typing import List, Tuple, Iterable

import cv2
import h5py
import numpy as np
import openslide
from matplotlib import pyplot as plt
from shapely.geometry import Polygon
from shapely.strtree import STRtree
from skimage.io import imshow

from img.filter.base_filter import FilterData, FilterType
from img.filter.kmeans_filter import KMeansFilterData
from img.filter.skimage_threshold import SkimageThresholdParams, SkimageThresholdType
from img.ndimagedata import NdImageData
from img.ndimagedata_utils import imgresize, create_empty_image
from img.proc.convert import pilimg_to_ndimg
from img.proc.img_mode_convert import convert_ndimg2
from img.proc.threshold.skimage_threshold import ndimg_to_skimage_threshold_range
from img.proc.threshold.threshold import ndimg_to_thresholded_ndimg
from common_shapely.shapely_utils import locate, scale_at_origin, get_polygon_bbox_pos, get_polygon_bbox_size
from slide_viewer.ui.odict.deep.model import AnnotationModel

def create_polygon_image(polygon: Polygon, color_mode: str, color=None, create_mask=True) -> NdImageData:
    nrows, ncols = get_polygon_bbox_size(polygon)
    img = create_empty_image(nrows, ncols, color_mode)
    if color is not None:
        points = polygon.boundary.coords
        points = np.array(points, dtype=np.int32).reshape((1, -1, 2), order='C')
        cv2.fillPoly(img.ndimg, points, color)
    if create_mask:
        img_boolean_mask = create_polygon_image(polygon, 'L', 255, create_mask=False).ndimg
    else:
        img_boolean_mask = None
    return NdImageData(img.ndimg, color_mode, img_boolean_mask)


def get_polygon_bbox_image_view(img: np.ndarray, polygon: Polygon) -> np.ndarray:
    # minx, miny, maxx, maxy = tuple(int(b) for b in polygon.bounds)
    x, y = get_polygon_bbox_pos(polygon)
    nrows, ncols = get_polygon_bbox_size(polygon)
    polygon_ndimg = img[y:y + nrows, x:x + ncols]
    return polygon_ndimg


def draw_source_on_target(target: NdImageData, target_mask_polygon: Polygon, source: NdImageData) -> None:
    target_region = get_polygon_bbox_image_view(target.ndimg, target_mask_polygon)
    source_ = imgresize(source, target_region.shape[:2])
    source_ = convert_ndimg2(source_, target.color_mode)
    # imgshow(source_.ndimg, 'prepared source image')
    # imgshow(target_region, 'Target(canvas)')
    # TODO target may have mask too, combine it with source_ mask through AND?
    cv2.subtract(target_region, target_region, target_region, mask=source_.bool_mask_ndimg)
    # imgshow(target_region, 'Target(canvas) after substract')
    cv2.add(source_.ndimg, target_region, target_region, mask=source_.bool_mask_ndimg)
    # imgshow(target_region, 'Target(canvas) result')
    # imgshow(target.ndimg, 'Target(canvas) resulting img')
    pass


def get_slide_polygon_bbox_rgb_region(slide: openslide.AbstractSlide, polygon: Polygon, level: int) -> NdImageData:
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


def process_filter(img: NdImageData, filter_data: FilterData) -> NdImageData:
    converted_ndimgdata = convert_ndimg2(img, 'L')
    params = SkimageThresholdParams(SkimageThresholdType.threshold_mean, {})
    threshold_range = ndimg_to_skimage_threshold_range(params, converted_ndimgdata)
    return ndimg_to_thresholded_ndimg(threshold_range, converted_ndimgdata)


def create_annotation_polygon_image(slide: openslide.AbstractSlide,
                                    annotation: AnnotationModel, annotation_geom: Polygon, polygon: Polygon,
                                    zlayers_rtrees: List[STRtree]) -> NdImageData:
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
    target = get_polygon_bbox_image_view(target_.ndimg, target_polygon)
    return NdImageData(target, target_.color_mode, target_.bool_mask_ndimg)


def create_layer_polygon_image(slide: openslide.AbstractSlide, polygon: Polygon, level: int,
                               zlayers_rtrees: List[STRtree]) -> NdImageData:
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
            print(f"Ignoring not Polygon intersection ${intersecting_geom_intersection}")
            continue
        intersecting_geom_intersection_ = scale_at_origin(locate(intersecting_geom_intersection, polygon), level_scale)
        annotation_polygon_image = create_annotation_polygon_image(slide, intersecting_geom.annotation, intersecting_geom,
                                                                   intersecting_geom_intersection_, zlayers_rtrees[:-1])
        draw_source_on_target(polygon_img, intersecting_geom_intersection_, annotation_polygon_image)

    return polygon_img

def npz_imgshow(file_path: str, slice_from, slice_to=None):
    npzfile = np.load(file_path)
    file_names = npzfile.files[slice_from: slice_to]
    arrs = [npzfile[file_name] for file_name in file_names]
    # imgshow(np.vstack(arrs))
    cols = 10
    rows = ceil(len(arrs) / cols)
    for i, arr in enumerate(arrs):
        ax = plt.subplot(rows, cols, i + 1)
        ax.axis('off')
        plt.imshow(arr)
    plt.show()