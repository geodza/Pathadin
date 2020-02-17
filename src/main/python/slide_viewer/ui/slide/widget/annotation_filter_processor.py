from concurrent.futures import Future, ThreadPoolExecutor
from itertools import product
from math import ceil
from typing import Tuple, Optional, Callable, Union, cast

import cv2
import numpy as np
import openslide
import skimage
import skimage.color
import skimage.measure
from PyQt5.QtCore import QObject, pyqtSignal, QPoint, QSize
from PyQt5.QtGui import QPixmapCache, QPixmap, QPolygon
from cachetools.keys import hashkey
from dataclasses import dataclass

from img.filter.base_filter import FilterData, ThresholdFilterResults, FilterResults2
from img.filter.keras_model import KerasModelFilterResults, KerasModelFilterData
from img.filter.kmeans_filter import KMeansFilterData, KMeansFilterResults
from img.filter.manual_threshold import ManualThresholdFilterData, HSVManualThresholdFilterData, \
    GrayManualThresholdFilterData
from img.filter.nuclei import NucleiFilterData, NucleiFilterResults
from img.filter.positive_pixel_count import PositivePixelCountFilterResults, PositivePixelCountFilterData
from img.filter.skimage_threshold import SkimageAutoThresholdFilterData, SkimageThresholdParams, \
    SkimageMinimumThresholdFilterData, SkimageMeanThresholdFilterData
from common_image.ndimagedata import NdImageData
from common_image.img_object_convert import pilimg_to_ndimg
from common_image_qt.core import ndimg_to_qimg, ndimg_to_bitmap
from common_image.hist import ndimg_to_hist
from img.proc.hist_html import build_histogram_html
from common_image.img_mode_convert import convert_ndimg, convert_ndarray
from img.proc.keras_model import KerasModelParams
from img.proc.kmeans import img_to_kmeans_quantized_img, KMeansParams
from img.proc.mask import build_mask
from img.proc.nuclei import NucleiParams, ndimg_to_nuclei_seg_mask
from img.proc.positive_pixel_count import PositivePixelCountParams, positive_pixel_count2
from img.proc.region import RegionData, read_region, deshift_points, rescale_points
from img.proc.threshold.skimage_threshold import ndimg_to_skimage_threshold_range
from common_image.threshold import ndimg_to_thresholded_ndimg
from slide_viewer.cache_config import cache_lock, cache_key_func, pixmap_cache_lock, cache_, gcached, add_to_global_pending, get_from_global_pending, \
    is_in_global_pending, remove_from_global_pending, closure_nonhashable
from common.debounce import debounce
from slide_viewer.common.slide_helper import SlideHelper
from common_qt.abcq_meta import ABCQMeta
from common_qt.qobjects_convert_util import ituple_to_qpoint, qpoint_to_ituple
from slide_viewer.ui.odict.deep.model import AnnotationModel
from slide_viewer.ui.slide.widget.interface.annotation_pixmap_provider import AnnotationItemPixmapProvider
from slide_viewer.ui.slide.widget.interface.annotation_service import AnnotationService
from slide_viewer.ui.slide.widget.interface.filter_model_provider import FilterModelProvider
from slide_viewer.ui.slide.widget.interface.slide_path_provider import SlidePathProvider


# (row,col)->(x,y)
def grid_pos_to_source_pos(grid_pos: Tuple[int, int], grid_length: int) -> Tuple[int, int]:
    x = grid_pos[1] * grid_length
    y = grid_pos[0] * grid_length
    return x, y


def grid_flat_pos_to_grid_pos(grid_flat_pos: int, grid_nrows: int) -> Tuple[int, int]:
    row = grid_flat_pos // grid_nrows
    # col = grid_flat_pos - row * grid_nrows
    col = grid_flat_pos % grid_nrows
    return (row, col)


# row,col
def grid_flat_pos_range(source_size: Tuple[int, int], grid_length: int):
    sw, sh = source_size
    gw, gh = grid_length, grid_length
    cols = ceil(sw / gw)
    rows = ceil(sh / gh)
    return range(rows * cols)


def pos_to_rect_coords(pos: Tuple[int, int], grid_length: int) -> Tuple[int, int, int, int]:
    return pos[0], pos[1], pos[0] + grid_length, pos[1] + grid_length


# row,col
def grid_pos_range(source_size: Tuple[int, int], grid_length: int):
    sw, sh = source_size
    gw, gh = grid_length, grid_length
    cols = ceil(sw / gw)
    rows = ceil(sh / gh)
    return product(range(rows), range(cols))


# x,y
def pos_range(source_size: Tuple[int, int], grid_length: int, x_offset: int = 0, y_offset: int = 0):
    sw, sh = source_size
    gw, gh = grid_length, grid_length
    cols = ceil(sw / gw)
    rows = ceil(sh / gh)
    return ((x_offset + col * grid_length, y_offset + row * grid_length) for row in range(rows) for col in range(cols))


def build_region_data(slide_path: str, model: AnnotationModel, filter_level: int) -> RegionData:
    origin_point = model.geometry.origin_point
    points = tuple(model.geometry.points)
    return RegionData(slide_path, filter_level, origin_point, points, model.geometry.annotation_type)


def read_masked_region(rd: RegionData) -> NdImageData:
    pilimg = read_region(rd)
    level0_qsize = QPolygon([ituple_to_qpoint(p) for p in rd.points]).boundingRect().size()
    sx, sy = pilimg.width / level0_qsize.width(), pilimg.height / level0_qsize.height()
    ndimg = pilimg_to_ndimg(pilimg)
    points = deshift_points(rd.points, rd.origin_point)
    points = rescale_points(points, sx, sy)
    # ituples = ituples_to_polygon_ituples(rd.points)
    mask = build_mask(ndimg.ndimg.shape, points, rd.annotation_type, background_color=0, color=255)
    # (0,0,0,0) for rgba means transparent
    masked_ndimg = cv2.bitwise_and(ndimg.ndimg, ndimg.ndimg, mask=mask)
    # ndimg.ndimg = mask_ndimg(ndimg.ndimg, points, rd.annotation_type)
    ndimg.ndimg = masked_ndimg
    # mask = cv2.bitwise_not(mask)
    ndimg.bool_mask_ndimg = mask != 0
    return ndimg


@gcached
def kmeans_filter(rd: RegionData, params: KMeansParams) -> KMeansFilterResults:
    ndimg = read_masked_region(rd)
    img_to_kmeans_quantized_img_ = closure_nonhashable(hashkey(rd), ndimg, img_to_kmeans_quantized_img)
    qantized_ndimg = img_to_kmeans_quantized_img_(params)
    hist = ndimg_to_hist(qantized_ndimg)
    hist_html = build_histogram_html(hist.sorted_most_freq_colors, hist.sorted_most_freq_colors_counts)
    qimg = ndimg_to_qimg(qantized_ndimg)
    res = KMeansFilterResults(qimg, ndimg.bool_mask_ndimg, hist_html)
    return res


@gcached
def nuclei_filter(rd: RegionData, params: NucleiParams) -> NucleiFilterResults:
    ndimg = read_masked_region(rd)
    seg_mask = ndimg_to_nuclei_seg_mask(ndimg, params)
    region_props = skimage.measure.regionprops(seg_mask.ndimg)
    labeled_ndimg = skimage.color.label2rgb(seg_mask.ndimg, ndimg.ndimg, bg_label=0)
    labeled_ndimg = skimage.util.img_as_ubyte(labeled_ndimg, force_copy=True)
    qimg = ndimg_to_qimg(NdImageData(labeled_ndimg, "RGB", ndimg.bool_mask_ndimg))
    return NucleiFilterResults(qimg, ndimg.bool_mask_ndimg, len(region_props))


# @gcached
def load_keras_model(model_path: str):
    from tensorflow.python.keras.saving import load_model
    keras_model = load_model(model_path)
    return keras_model


@gcached
def keras_model_filter(rd: RegionData, params: KerasModelParams) -> KerasModelFilterResults:
    keras_model = load_keras_model(params.model_path)
    tile_shape = keras_model.input_shape[1:]
    grid_length = tile_shape[0]
    overlap_length = grid_length // 2
    overlap_length = 0
    data = rd
    polygon = QPolygon([ituple_to_qpoint(p) for p in data.points])
    original_top_left = ituple_to_qpoint(data.origin_point) + polygon.boundingRect().topLeft()
    top_left = original_top_left - QPoint(overlap_length, overlap_length)
    top_left_shift = original_top_left - top_left
    pos = qpoint_to_ituple(top_left)
    original_size = polygon.boundingRect().size()
    size = original_size + QSize(overlap_length * 2, overlap_length * 2)
    rows, cols = size.height() / grid_length, size.width() / grid_length
    width, height = ceil(cols) * grid_length, ceil(rows) * grid_length
    sh = SlideHelper(rd.img_path)
    level = data.level
    if level is None or level == '':
        level = sh.get_levels()[min(2, len(sh.get_levels()) - 1)]
    level = int(level)
    level_downsample = sh.level_downsamples[level]
    # width_fit_grid_length = ceil(original_size.width() / level_downsample / grid_length) * level_downsample *grid_length
    # height_fit_grid_length = ceil(original_size.height() / level_downsample / grid_length) * level_downsample *grid_length
    # width_fit_scale = width_fit_grid_length / original_size.width()
    # height_fit_scale = height_fit_grid_length / original_size.height()
    level_width, level_height = ceil(width / level_downsample), ceil(height / level_downsample)
    width, height = ceil(level_width / grid_length) * grid_length, ceil(level_height / grid_length) * grid_length
    size = (width, height)
    with openslide.OpenSlide(rd.img_path) as f:
        pilimg=f.read_region(pos, level, size)

    #     pilimg.resize(())
    # transform = QTransform().translate(-polygon.boundingRect().left(), -polygon.boundingRect().top())\
    #     .scale(1/ level_downsample/grid_length, 1/ level_downsample/grid_length)
    # p1=transform.map(QPolygonF(polygon))
    # ws,hs=width_fit_grid_length/p1.boundingRect().size().width(),height_fit_grid_length/p1.boundingRect().size().height()
    # polygon_fit_grid=QTransform().scale(ws,hs).translate(polygon.boundingRect().left(), polygon.boundingRect().top())\
    #     .map(p1)
    # ws,hs=resultsize.width(),resultsize.height()
        # .translate(polygon.boundingRect().left(),polygon.boundingRect().top())
    # polygon_fit_grid=transform.map(polygon)
    # points_fit_grid_length=tuple(qpoint_to_ituple(p) for p in polygon_fit_grid)
    # ndimg=read_masked_region(rd._replace(points=points_fit_grid_length))

    # pilimg = load_region(data.img_path, pos, level, size)
    ndimg = pilimg_to_ndimg(pilimg)
    # ndimg = convert_ndimg2(ndimg, "RGB")
    region_mask = np.empty((height, width, 1), dtype='uint8')
    for row, col in grid_pos_range(size, grid_length):
        # TODO mirror if border tile
        # TODO img conversions in layer of model
        x, y = grid_pos_to_source_pos((row, col), grid_length)
        tile = ndimg.ndimg[y:y + grid_length, x:x + grid_length]
        tile = convert_ndarray(tile, "RGBA", "RGB")
        tile = tile / 255
        tile_batch = np.array([tile])
        tile_mask_batch = keras_model.predict(tile_batch)
        tile_mask = tile_mask_batch[0]
        # tile_mask = tile_mask>=0.5
        # tile_mask = tile_mask/2
        # io.imshow(np.squeeze(tile_mask))
        tile_mask = skimage.util.img_as_ubyte(tile_mask)
        region_mask[y:y + grid_length, x:x + grid_length] = tile_mask

    # io.imshow(np.squeeze(region_mask))
    # io.show()
    region_mask = region_mask[top_left_shift.y():top_left_shift.y() + original_size.height(),
                  top_left_shift.x():top_left_shift.x() + original_size.width(), ...]
    region_mask = region_mask[:level_height, :level_width, ...]
    # io.imshow(np.squeeze(region_mask))
    # io.show()
    # io.imshow(np.squeeze(region_mask))
    # io.show()
    mask_color = np.array([0, 255, 0, 0], dtype='uint8')
    region_mask_rgba = np.tile(mask_color, region_mask.shape)
    region_mask_rgba[..., 3] = np.squeeze(region_mask)
    # io.imshow(np.squeeze(region_mask_rgba))
    # io.show()
    qimg = ndimg_to_qimg(NdImageData(region_mask_rgba, "RGBA", ndimg.bool_mask_ndimg))
    return KerasModelFilterResults(qimg, ndimg.bool_mask_ndimg)


# if __name__ == '__main__':
#     slide_path = r"D:\slide_cbir_47\temp\slides\slide-2019-09-19T18-08-52-R28-S3.mrxs"
#     ds = r"."
#     grid_length = 256
#     model_path = r"D:\dieyepy\src\main\python\256\unet_model_19_01_2020.h5"
#     rd = RegionData(slide_path, 0, (0, 0), ((41728, 63232), (42008, 63512)), AnnotationType.RECT)
#     fr = keras_model_filter(rd, KerasModelParams(model_path))
#     print(fr)


def threshold_filter(img: NdImageData, threshold_range: tuple) -> ThresholdFilterResults:
    thresholded_ndimg = ndimg_to_thresholded_ndimg(img, threshold_range)
    hist = ndimg_to_hist(thresholded_ndimg)
    hist_html = build_histogram_html(hist.sorted_most_freq_colors, hist.sorted_most_freq_colors_counts)
    qimg = ndimg_to_qimg(thresholded_ndimg)
    res = ThresholdFilterResults(qimg, thresholded_ndimg.bool_mask_ndimg, hist_html)
    return res


@gcached
def manual_threshold_filter(rd: RegionData, color_mode: str, threshold_range: tuple):
    ndimg = read_masked_region(rd)
    converted_ndimg = closure_nonhashable(hashkey(rd), ndimg, convert_ndimg)(color_mode)
    return threshold_filter(converted_ndimg, threshold_range)


@gcached
def skimage_threshold_filter(rd: RegionData, params: SkimageThresholdParams):
    ndimg = read_masked_region(rd)
    converted_ndimg = closure_nonhashable(hashkey(rd), ndimg, convert_ndimg)("L")
    threshold_range = ndimg_to_skimage_threshold_range(params, converted_ndimg)
    return threshold_filter(converted_ndimg, threshold_range)


@gcached
def positive_pixel_count_filter(rd: RegionData, params: PositivePixelCountParams):
    ndimg = read_masked_region(rd)
    converted_ndimg = closure_nonhashable(hashkey(rd), ndimg, convert_ndimg)("RGB")
    ndimg, stats = positive_pixel_count2(converted_ndimg, params)
    qimg = ndimg_to_qimg(ndimg)
    res = PositivePixelCountFilterResults(qimg, ndimg.bool_mask_ndimg, stats)
    return res


def create_filter_task(func, *args, **kwargs):
    def f():
        return func(*args, **kwargs)

    func_cache_key = cache_key_func(func.__name__)(*args, **kwargs)
    return f, func_cache_key


def create_filter_task2(region_data: RegionData, filter_data: FilterData):
    if isinstance(filter_data, KMeansFilterData):
        filter_task, cache_key = create_filter_task(kmeans_filter, region_data, filter_data.kmeans_params)
        # cache_key = cache_key_func(kmeans_filter.__name__)(region_data, filter_data.kmeans_params)
        # print("search", str(cache_key))
    elif isinstance(filter_data, NucleiFilterData):
        filter_task, cache_key = create_filter_task(nuclei_filter, region_data, filter_data.nuclei_params)
    elif isinstance(filter_data, ManualThresholdFilterData):
        if isinstance(filter_data, HSVManualThresholdFilterData):
            filter_task, cache_key = create_filter_task(manual_threshold_filter, region_data,
                                                        filter_data.color_mode.name,
                                                        filter_data.hsv_range)
        elif isinstance(filter_data, GrayManualThresholdFilterData):
            filter_task, cache_key = create_filter_task(manual_threshold_filter, region_data,
                                                        filter_data.color_mode.name,
                                                        filter_data.gray_range)
        else:
            raise ValueError()
    elif isinstance(filter_data, SkimageAutoThresholdFilterData):
        if isinstance(filter_data, SkimageMinimumThresholdFilterData):
            params = SkimageThresholdParams(filter_data.skimage_threshold_type,
                                            filter_data.skimage_threshold_minimum_params)
            filter_task, cache_key = create_filter_task(skimage_threshold_filter, region_data, params)
        elif isinstance(filter_data, SkimageMeanThresholdFilterData):
            params = SkimageThresholdParams(filter_data.skimage_threshold_type, None)
            filter_task, cache_key = create_filter_task(skimage_threshold_filter, region_data, params)
        else:
            raise ValueError()
    elif isinstance(filter_data, PositivePixelCountFilterData):
        filter_task, cache_key = create_filter_task(positive_pixel_count_filter, region_data,
                                                    filter_data.positive_pixel_count_params)
    elif isinstance(filter_data, KerasModelFilterData):
        filter_task, cache_key = create_filter_task(keras_model_filter, region_data,
                                                    filter_data.keras_model_params)
    else:
        raise ValueError()
    return filter_task, cache_key


@dataclass
class AnnotationFilterProcessor(QObject, AnnotationItemPixmapProvider, metaclass=ABCQMeta):
    pool: ThreadPoolExecutor
    slide_path_provider: Union[SlidePathProvider, Callable[[], str]]
    annotation_service: AnnotationService
    filter_model_provider: Union[FilterModelProvider, Callable[[str], FilterData]]
    filterResultsChange = pyqtSignal(str, FilterResults2)

    def __post_init__(self):
        QObject.__init__(self)
        self.schedule_filter_task = debounce(0.5)(self.schedule_filter_task_to_pool)
        self.filterResultsChange.connect(self.on_filter_results_change)
        self.id = None  # debug purpose

    def on_filter_results_change(self, annotation_id: str, filter_results: FilterResults2) -> None:
        self.annotation_service.edit_filter_results(annotation_id, filter_results)

    def get_pixmap(self, annotation_id: str, ready_callback: Callable[[], None]) -> Optional[Tuple[int, QPixmap]]:
        annotation_model = self.annotation_service.get(annotation_id)
        if not annotation_model or annotation_model.filter_id is None:
            return None
        filter_id = annotation_model.filter_id
        filter_level = annotation_model.filter_level
        filter_data = self.filter_model_provider.get_filter_model(filter_id) if isinstance(self.filter_model_provider,
                                                                                           FilterModelProvider) else self.filter_model_provider(
            filter_id)
        if filter_data is None:
            return None
        slide_path = self.slide_path_provider.get_slide_path() if isinstance(self.slide_path_provider,
                                                                             SlidePathProvider) else self.slide_path_provider()
        if slide_path is None:
            return None
        region_data = build_region_data(slide_path, annotation_model, filter_level)
        filter_task, cache_key = create_filter_task2(region_data, filter_data)
        with pixmap_cache_lock, cache_lock:
            pixmap = QPixmapCache.find(str(cache_key))
            filter_results = cache_.get(cache_key)
            if pixmap and filter_results:
                self.annotation_service.edit_filter_results(annotation_id, filter_results)
                return filter_level, pixmap
            elif cache_key in cache_:
                filter_results: FilterResults2 = cast(FilterResults2, cache_.get(cache_key))
                pixmap = QPixmap.fromImage(filter_results.img)
                if filter_results.bool_mask_ndimg is not None:
                    bitmap = ndimg_to_bitmap(filter_results.bool_mask_ndimg)
                    pixmap.setMask(bitmap)
                QPixmapCache.insert(str(cache_key), pixmap)
                self.annotation_service.edit_filter_results(annotation_id, filter_results)
                ready_callback()
                return filter_level, pixmap
            else:
                self.schedule_filter_task(annotation_id, filter_task, cache_key, ready_callback)
                return None

    def schedule_filter_task_to_pool(self, annotation_id: str, filter_task: Callable[[], FilterResults2], task_key: str,
                                     ready_callback: Callable[[], None]):
        # print(f"schedule try: {self.id}, {self}")
        def done_func(ff: Future):
            try:
                ff.result()
                ready_callback()
            except Exception as e:
                # QMessageBox.critical(None,"Error in filters", str(e))
                raise e

        with cache_lock:
            if not is_in_global_pending(task_key):
                # print(f"schedule: {self.id}")
                future = self.pool.submit(self.perform_task, annotation_id, filter_task, task_key, ready_callback)
                add_to_global_pending(task_key, future)
                future.add_done_callback(done_func)
            else:
                future = get_from_global_pending(task_key)
                future.add_done_callback(done_func)

    def perform_task(self, annotation_id: str, filter_task: Callable[[], FilterResults2], task_key: str, ready_callback: Callable[[], None]) -> None:
        filter_results = filter_task()
        with cache_lock:
            if self:
                self.filterResultsChange.emit(annotation_id, filter_results)
                remove_from_global_pending(task_key)
                ready_callback()
