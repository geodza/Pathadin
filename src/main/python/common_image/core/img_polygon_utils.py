import cv2
import numpy as np
from shapely.geometry import Polygon

from common_image.core.mode_convert import convert_ndimg
from common_image.model.ndimagedata import NdImageData
from common_image.core.empty import create_empty_ndimg
from common_image.core.resize import resize_ndimg
from common_shapely.shapely_utils import get_polygon_bbox_size, get_polygon_bbox_pos


def create_polygon_image(polygon: Polygon, color_mode: str, color=None, create_mask=True) -> NdImageData:
    nrows, ncols = get_polygon_bbox_size(polygon)
    img = create_empty_ndimg(nrows, ncols, color_mode)
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


def draw_source_on_target_polygon(target: NdImageData, target_mask_polygon: Polygon, source: NdImageData) -> None:
    target_region = get_polygon_bbox_image_view(target.ndimg, target_mask_polygon)
    source_ = resize_ndimg(source, target_region.shape[:2])
    source_ = convert_ndimg(source_, target.color_mode)
    # imgshow(source_.ndimg, 'prepared source image')
    # imgshow(target_region, 'Target(canvas)')
    # TODO target may have mask too, combine it with source_ mask through AND?
    cv2.subtract(target_region, target_region, target_region, mask=source_.bool_mask_ndimg)
    # imgshow(target_region, 'Target(canvas) after substract')
    cv2.add(source_.ndimg, target_region, target_region, mask=source_.bool_mask_ndimg)
    # imgshow(target_region, 'Target(canvas) result')
    # imgshow(target.ndimg, 'Target(canvas) resulting img')
    pass