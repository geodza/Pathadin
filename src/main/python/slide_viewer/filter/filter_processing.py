from typing import Optional, Tuple

import numpy as np
from PIL import Image
from PyQt5.QtGui import QPolygon, QImage

from slide_viewer.cache_config import gcached
from slide_viewer.common.slide_helper import SlideHelper
from slide_viewer.common_qt.qobjects_convert_util import tuple_to_qpoint, tuples_to_qpoints, \
    qpoints_to_tuples, qpoint_to_tuple
from slide_viewer.filter.kmeans import process_kmeans_filter
from slide_viewer.filter.mask import mask_ndimg
from slide_viewer.filter.nuclei import process_nuclei_filter
from slide_viewer.filter.quantization import process_quantization_filter
from slide_viewer.filter.threshold.threshold import process_threshold_filter
from slide_viewer.ui.common.img.img_mode_convert import convert_pilimage, convert_ndimg
from slide_viewer.ui.common.img.img_object_convert import expose_ndarray_to_qimage, expose_pilimage_buffer_to_ndarray
from slide_viewer.ui.model.filter.base_filter import FilterData, FilterResults
from slide_viewer.ui.model.filter.kmeans_filter import KMeansFilterData
from slide_viewer.ui.model.filter.nuclei import NucleiFilterData
from slide_viewer.ui.model.filter.quantization_filter import QuantizationFilterData
from slide_viewer.ui.model.filter.region_data import RegionData
from slide_viewer.ui.model.filter.threshold_filter import ThresholdFilterData


@gcached("load_region")
def load_region(img_path: str, pos: Tuple[int, int] = (0, 0), level: Optional[int] = None,
                size: Tuple[int, int] = None) -> Image.Image:
    sh = SlideHelper(img_path)
    if level is None:
        level = sh.get_levels()[min(2, len(sh.get_levels()) - 1)]
    level = int(level)
    if level < 0:
        level = sh.get_levels()[-level]
    # TODO add literals for level like MAX_LEVEL, AUTO_LEVEL(about memory considerations)
    print(f"load_region on level: {level}")
    level_downsample = sh.get_downsample_for_level(level)
    if size is not None:
        size = (size[0] / level_downsample, size[1] / level_downsample)
    region = sh.read_region_pilimage(pos, level, size)
    return region


@gcached("build_source_")
def build_source_(data: RegionData) -> Image.Image:
    if data.points is not None and data.origin_point is not None:
        polygon = QPolygon([tuple_to_qpoint(p) for p in data.points])
        top_left = tuple_to_qpoint(data.origin_point) + polygon.boundingRect().topLeft()
        pos = qpoint_to_tuple(top_left)
        size = polygon.boundingRect().size()
        size = (size.width(), size.height())
        return load_region(data.img_path, pos, data.level, size)
    else:
        return load_region(data.img_path)


# @gcached("mask_source_")
# func_ is not for purpose of reusability, it is only for purpose of 1) cachability 2) order of steps
# TODO mask_source_ contains only data-cache and sequence logic
# TODO mask_source contains image-processing logic
def mask_source_(data: RegionData) -> FilterResults:
    region = build_source_(data)
    region = FilterResults(region, region.mode, None)
    if data.points is None:
        return region
    # TODO pilimg.tobytes() is not just returning buffer
    qpoints = tuple(tuples_to_qpoints(data.points))
    top_left = QPolygon(qpoints).boundingRect().topLeft()
    qpoints0 = [p - top_left for p in qpoints]
    points0 = tuple(qpoints_to_tuples(qpoints0))
    region.color_mode = region.img.mode
    region.img = expose_pilimage_buffer_to_ndarray(region.img)
    region.img = mask_ndimg(region.img, points0)
    return region


# @gcached("convert_source_")
def convert_source_(region_data: RegionData, source_convert_mode: Optional[str]) -> FilterResults:
    region = mask_source_(region_data)
    if source_convert_mode is None:
        return region

    return convert_filter_results(region, source_convert_mode)


def convert_filter_results(fr: FilterResults, required_mode: str) -> FilterResults:
    if isinstance(fr.img, Image.Image):
        fr.img = convert_pilimage(fr.img, required_mode)
        fr.color_mode = required_mode
        return fr
    elif isinstance(fr.img, np.ndarray):
        fr.img = convert_ndimg(fr.img, fr.color_mode, required_mode)
        fr.color_mode = required_mode
        return fr
    else:
        raise ValueError(f"Unsupported img type for convert_filter_results: {fr.img}")


def filter_img(fr: FilterResults, filter_data: FilterData) -> FilterResults:
    fr.filter_type = filter_data.filter_type
    if isinstance(filter_data, ThresholdFilterData):
        return process_threshold_filter(fr, filter_data)
    elif isinstance(filter_data, QuantizationFilterData):
        return process_quantization_filter(fr, filter_data)
    elif isinstance(filter_data, KMeansFilterData):
        return process_kmeans_filter(fr, filter_data)
    elif isinstance(filter_data, NucleiFilterData):
        return process_nuclei_filter(fr, filter_data)


# @gcached("filter_source_")
def filter_source_(region_data: RegionData, source_convert_mode: Optional[str],
                   filter_data: FilterData) -> FilterResults:
    region = convert_source_(region_data, source_convert_mode)
    if filter_data is None:
        return region
    return filter_img(region, filter_data)


# @gcached("mask_result_")
def mask_result_(region_data: RegionData, source_convert_mode: Optional[str], filter_data: FilterData) -> FilterResults:
    # region = filter_source_(region_data, source_convert_mode, filter_data)
    region = filter_source_(region_data, source_convert_mode, filter_data)
    if isinstance(region.img, Image.Image):
        region.img = region.img.mode
        region.img = expose_pilimage_buffer_to_ndarray(region.img)
    elif isinstance(region.img, np.ndarray):
        pass
    else:
        raise ValueError(f"Unsupported img type for mask_result: {region.img}")
    if region_data.points is None:
        return region
    qpoints = tuple(tuples_to_qpoints(region_data.points))
    top_left = QPolygon(qpoints).boundingRect().topLeft()
    qpoints0 = [p - top_left for p in qpoints]
    points0 = tuple(qpoints_to_tuples(qpoints0))
    masked_ndimg = mask_ndimg(region.img, points0)
    region.img = masked_ndimg
    return region


@gcached("qimage_result_")
def qimage_result_(region_data: RegionData, source_convert_mode: Optional[str],
                   filter_data: FilterData) -> FilterResults:
    region = mask_result_(region_data, source_convert_mode, filter_data)
    if isinstance(region.img, QImage):
        qimg = region.img
    elif isinstance(region.img, Image.Image):
        qimg = region.img.toqimage()
    else:
        if region.color_mode == 'RGBA':
            format = QImage.Format_RGBA8888
        elif region.color_mode == 'RGB':
            format = QImage.Format_RGB888
        elif region.color_mode == 'L':
            format = QImage.Format_Grayscale8
        else:
            raise ValueError(f"Unsupported img color mode: {region.color_mode}")
        qimg = expose_ndarray_to_qimage(region.img, format)
        qimg.__dict__['ndimg'] = region.img
    region.img = qimg
    # region_arr = expose_qimage_buffer_to_ndarray(region_qimage)
    # mask = region_qimage.createMaskFromColor(Qt.black)
    # arr = expose_qimage_buffer_to_ndarray(mask)
    # qimage_to_pillowimage(mask).show()
    return region

# @gcached("convert_result_convert_ndimg")
# def convert_result_(region_data: RegionData, source_convert_mode: Optional[str],
#                     filter_data: FilterData, result_convert_mode: Optional[str]) -> FilterResults:
#     region = mask_result_(region_data, source_convert_mode, filter_data)
#     if result_convert_mode is None:
#         return region
#     converted = convert_ndimg(region.ndimg, region.color_mode, result_convert_mode)
#     region.ndimg = converted
#     region.color_mode = result_convert_mode
#     return region

# def build_source_background(self):
#     if self.data.filter_data is None or self.data.filter_data.source_mask_color is None or self.source_pilimg is None:
#         return
#     bg_color = self.data.filter_data.source_mask_color
#
#     background_color = QColor(bg_color)
#     if background_color:
#         required_mode = self.source_pilimg.mode
#         if self.data.filter_data.result_mask_color == bg_color and self.result_background_pilimg is not None and \
#                 self.result_background_pilimg.mode == required_mode:
#             self.source_background_img = self.result_background_img
#             self.source_background_pilimg = self.result_background_pilimg
#             return
#         mode = "RGBA"
#         if required_mode != mode:
#             color_pilimg = Image.new(mode, (1, 1), color=background_color.getRgb())
#             color_pilimg = convert_pilimage(color_pilimg, required_mode)
#             color_arr = expose_pilimage_buffer_to_ndarray(color_pilimg)
#         else:
#             color_arr = np.array(background_color.getRgb(), dtype=np.uint8, order='C').reshape((1, 1, - 1))
#         r, c, *a = self.source_img.shape
#         self.source_background_img = np.tile(color_arr, r * c).reshape((r, c, -1))
#         self.source_background_img = cv2.bitwise_and(self.source_background_img, self.source_background_img,
#                                                      mask=cv2.bitwise_not(self.mask_img))
#         self.source_background_pilimg = expose_ndarray_buffer_to_pillowimage(self.source_background_img,
#                                                                              required_mode)
#
# def apply_background_to_source(self):
#     if self.source_img is None or self.source_background_img is None:
#         return
#     cv2.add(self.source_img, self.source_background_img, self.source_img)
