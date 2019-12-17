from concurrent.futures import Future, ThreadPoolExecutor
from concurrent.futures import Future, ThreadPoolExecutor
from functools import partial
from typing import Set, Tuple, Optional, Callable, Union, cast

import cachetools
import skimage
import skimage.color
import skimage.measure
from PyQt5.QtCore import QObject, pyqtSignal, Qt
from PyQt5.QtGui import QPixmapCache, QPixmap, QBitmap, QPainter, QPolygon, QPen, QBrush
from cachetools.keys import hashkey
from dataclasses import dataclass, field

from img.filter.base_filter import FilterData, ThresholdFilterResults, FilterResults2
from img.filter.kmeans_filter import KMeansFilterData, KMeansFilterResults
from img.filter.manual_threshold import ManualThresholdFilterData, HSVManualThresholdFilterData, \
    GrayManualThresholdFilterData
from img.filter.nuclei import NucleiFilterData, NucleiFilterResults
from img.filter.positive_pixel_count import PositivePixelCountFilterResults, PositivePixelCountFilterData
from img.filter.skimage_threshold import SkimageAutoThresholdFilterData, SkimageThresholdParams, \
    SkimageMinimumThresholdFilterData, SkimageMeanThresholdFilterData
from img.model import NdImageData, ituple
from img.proc.convert import pilimg_to_ndimg, ndimg_to_qimg
from img.proc.hist import ndimg_to_hist, HistParams
from img.proc.hist_html import build_histogram_html
from img.proc.img_mode_convert import convert_ndimg2
from img.proc.kmeans import img_to_kmeans_quantized_img, KMeansParams
from img.proc.mask import mask_ndimg
from img.proc.nuclei import NucleiParams, ndimg_to_nuclei_seg_mask
from img.proc.positive_pixel_count import PositivePixelCountParams, positive_pixel_count2
from img.proc.region import RegionData, read_region, deshift_points, rescale_points
from img.proc.threshold.skimage_threshold import ndimg_to_skimage_threshold_range
from img.proc.threshold.threshold import ndimg_to_thresholded_ndimg
from slide_viewer.cache_config import cache_lock, cache_key_func, pixmap_cache_lock, cache_, gcached
from slide_viewer.common.debounce import debounce
from slide_viewer.common_qt.abcq_meta import ABCQMeta
from slide_viewer.common_qt.qobjects_convert_util import ituples_to_qpoints, qsize_to_ituple, ituple_to_qsize, \
    ituple_to_qpoint
from slide_viewer.ui.model.annotation_type import AnnotationType
from slide_viewer.ui.odict.deep.model import AnnotationModel
from slide_viewer.ui.slide.widget.interface.annotation_pixmap_provider import AnnotationItemPixmapProvider
from slide_viewer.ui.slide.widget.interface.annotation_service import AnnotationService
from slide_viewer.ui.slide.widget.interface.filter_model_provider import FilterModelProvider
from slide_viewer.ui.slide.widget.interface.slide_path_provider import SlidePathProvider


def build_region_data(slide_path: str, model: AnnotationModel, filter_level: int) -> RegionData:
    # if model.geometry.annotation_type in (AnnotationType.RECT, AnnotationType.ELLIPSE, AnnotationType.LINE):
    #     # p1, p2 = model.geometry.points
    #     rect_polygon = QPolygon(QPolygon(tuples_to_qpoints(model.geometry.points)).boundingRect(), True)
    #     qpoints = tuple(rect_polygon)
    #     points = tuple(qpoints_to_tuples(qpoints))
    # else:
    #     points = tuple(model.geometry.points)
    #
    origin_point = model.geometry.origin_point
    points = tuple(model.geometry.points)
    return RegionData(slide_path, filter_level, origin_point, points, model.geometry.annotation_type)


def closure_nonhashable(hash_prefix: str, i, func):
    # def decor(method):
    #     return cachetools.cached(cache_, key=partial(hashkey, method.__name__, hash_prefix), lock=cache_lock)(method)

    def w(*args, **kwargs):
        return func(i, *args, **kwargs)

    cached_w = cachetools.cached(cache_, key=partial(hashkey, func.__name__, hash_prefix), lock=cache_lock)(w)

    return cached_w


def read_masked_region(rd: RegionData) -> NdImageData:
    pilimg = read_region(rd)
    level0_qsize = QPolygon([ituple_to_qpoint(p) for p in rd.points]).boundingRect().size()
    sx, sy = pilimg.width / level0_qsize.width(), pilimg.height / level0_qsize.height()
    ndimg = pilimg_to_ndimg(pilimg)
    points = deshift_points(rd.points, rd.origin_point)
    points = rescale_points(points, sx, sy)
    # ituples = ituples_to_polygon_ituples(rd.points)
    ndimg.ndimg = mask_ndimg(ndimg.ndimg, points, rd.annotation_type)
    return ndimg


@gcached
def kmeans_filter(rd: RegionData, params: KMeansParams) -> KMeansFilterResults:
    ndimg = read_masked_region(rd)
    img_to_kmeans_quantized_img_ = closure_nonhashable(hashkey(rd), ndimg, img_to_kmeans_quantized_img)
    qantized_ndimg = img_to_kmeans_quantized_img_(params)
    hist = ndimg_to_hist(HistParams(), qantized_ndimg)
    hist_html = build_histogram_html(hist.sorted_most_freq_colors, hist.sorted_most_freq_colors_counts)
    qimg = ndimg_to_qimg(qantized_ndimg)
    res = KMeansFilterResults(qimg, hist_html)
    return res


@gcached
def nuclei_filter(rd: RegionData, params: NucleiParams) -> NucleiFilterResults:
    ndimg = read_masked_region(rd)
    seg_mask = ndimg_to_nuclei_seg_mask(ndimg, params)
    region_props = skimage.measure.regionprops(seg_mask.ndimg)
    labeled_ndimg = skimage.color.label2rgb(seg_mask.ndimg, ndimg.ndimg, bg_label=0)
    labeled_ndimg = skimage.util.img_as_ubyte(labeled_ndimg, force_copy=True)
    qimg = ndimg_to_qimg(NdImageData(labeled_ndimg, "RGB"))
    return NucleiFilterResults(qimg, len(region_props))


def threshold_filter(img: NdImageData, threshold_range: tuple) -> ThresholdFilterResults:
    thresholded_ndimg = ndimg_to_thresholded_ndimg(threshold_range, img)
    hist = ndimg_to_hist(HistParams(), thresholded_ndimg)
    hist_html = build_histogram_html(hist.sorted_most_freq_colors, hist.sorted_most_freq_colors_counts)
    qimg = ndimg_to_qimg(thresholded_ndimg)
    res = ThresholdFilterResults(qimg, hist_html)
    return res


@gcached
def manual_threshold_filter(rd: RegionData, color_mode: str, threshold_range: tuple):
    ndimg = read_masked_region(rd)
    converted_ndimg = closure_nonhashable(hashkey(rd), ndimg, convert_ndimg2)(color_mode)
    return threshold_filter(converted_ndimg, threshold_range)


@gcached
def skimage_threshold_filter(rd: RegionData, params: SkimageThresholdParams):
    ndimg = read_masked_region(rd)
    converted_ndimg = closure_nonhashable(hashkey(rd), ndimg, convert_ndimg2)("L")
    threshold_range = ndimg_to_skimage_threshold_range(params, converted_ndimg)
    return threshold_filter(converted_ndimg, threshold_range)


@gcached
def positive_pixel_count_filter(rd: RegionData, params: PositivePixelCountParams):
    ndimg = read_masked_region(rd)
    converted_ndimg = closure_nonhashable(hashkey(rd), ndimg, convert_ndimg2)("RGB")
    ndimg, stats = positive_pixel_count2(converted_ndimg, params)
    qimg = ndimg_to_qimg(ndimg)
    res = PositivePixelCountFilterResults(qimg, stats)
    return res


@gcached
def region_data_to_bitmap(rd: RegionData, pixmap_size: ituple) -> QBitmap:
    bitmap = QBitmap(ituple_to_qsize(pixmap_size))
    level0_qsize = QPolygon([ituple_to_qpoint(p) for p in rd.points]).boundingRect().size()
    sx, sy = bitmap.width() / level0_qsize.width(), bitmap.height() / level0_qsize.height()
    points = deshift_points(rd.points, rd.origin_point)
    points = rescale_points(points, sx, sy)
    # bounding_rect = QPolygon(ituples_to_qpoints(points)).boundingRect()
    painter = QPainter(bitmap)
    pen = QPen(Qt.color0)
    brush = QBrush(Qt.color0)
    painter.setPen(pen)
    painter.setBrush(brush)
    painter.drawRect(bitmap.rect())
    brush.setColor(Qt.color1)
    pen.setColor(Qt.color1)
    painter.setPen(pen)
    painter.setBrush(brush)
    if rd.annotation_type is AnnotationType.RECT:
        painter.drawRect(bitmap.rect())
    elif rd.annotation_type is AnnotationType.ELLIPSE:
        painter.drawEllipse(bitmap.rect())
    elif rd.annotation_type is AnnotationType.POLYGON:
        qpoints = ituples_to_qpoints(points)
        painter.drawPolygon(QPolygon(qpoints))
    elif rd.annotation_type is AnnotationType.LINE:
        pen.setWidth(50)
        p1, p2 = ituples_to_qpoints(points)
        painter.drawLine(p1, p2)
    painter.end()
    return bitmap


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
    else:
        raise ValueError()
    return filter_task, cache_key


def build_global_pending_key(key: str):
    return 'pending__{}'.format(key)


def add_to_global_pending(key: str):
    cache_[build_global_pending_key(key)] = True


def is_in_global_pending(key: str):
    return build_global_pending_key(key) in cache_


def remove_from_global_pending(key: str):
    cache_.pop(build_global_pending_key(key), None)


@dataclass
class AnnotationFilterProcessor(QObject, AnnotationItemPixmapProvider, metaclass=ABCQMeta):
    pool: ThreadPoolExecutor
    slide_path_provider: Union[SlidePathProvider, Callable[[], str]]
    annotation_service: Union[AnnotationService, Callable[[str], AnnotationModel]]
    filter_model_provider: Union[FilterModelProvider, Callable[[str], FilterData]]
    pending: Set = field(default_factory=set)
    filterResultsChange = pyqtSignal(str, FilterResults2)
    updateAllViewsFunc: Callable = None

    def __post_init__(self):
        QObject.__init__(self)
        self.schedule_filter_task = debounce(0.5)(self.schedule_filter_task)
        self.filterResultsChange.connect(self.on_filter_results_change)
        self.id = None  # debug purpose

    def on_filter_results_change(self, annotation_id, filter_results: FilterResults2):
        self.annotation_service.edit_filter_results(annotation_id, filter_results)
        self.updateAllViewsFunc()

    def task(self, annotation_id, filter_task, task_key, ready_callback):
        filter_results = filter_task()
        with cache_lock:
            if self:
                self.filterResultsChange.emit(annotation_id, filter_results)
                remove_from_global_pending(task_key)
                ready_callback()

    def schedule_filter_task(self, annotation_id, filter_task, task_key, ready_callback):
        # print(f"schedule try: {self.id}, {self}")
        with cache_lock:
            if not is_in_global_pending(task_key):
                # print(f"schedule: {self.id}")
                add_to_global_pending(task_key)
                future = self.pool.submit(self.task, annotation_id, filter_task, task_key, ready_callback)

                def done_func(ff: Future):
                    try:
                        ff.result()
                    except Exception as e:
                        raise e

                future.add_done_callback(done_func)

    def get_pixmap(self, annotation_id: str, ready_callback) -> Optional[Tuple[int, QPixmap]]:
        annotation_model = self.annotation_service.get(annotation_id) \
            if isinstance(self.annotation_service, AnnotationService) else self.annotation_service(annotation_id)
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
                # ready_callback()
                return filter_level, pixmap
            elif cache_key in cache_:
                filter_results: FilterResults2 = cast(FilterResults2, cache_.get(cache_key))
                pixmap = QPixmap.fromImage(filter_results.img)
                pixmap_size = qsize_to_ituple(pixmap.size())
                bitmap = region_data_to_bitmap(region_data, pixmap_size)
                pixmap.setMask(bitmap)
                QPixmapCache.insert(str(cache_key), pixmap)
                # cache_[f"filter_results__{str(cache_key)}"] = filter_results
                self.annotation_service.edit_filter_results(annotation_id, filter_results)
                self.updateAllViewsFunc()
                # ready_callback()
                return filter_level, pixmap
            else:
                # if self.id==0:
                #     print("0 sleep before pre")
                # time.sleep(1)
                # print(f"schedule pre: {self.id} {id(self.schedule_filter_task)}")
                # There might be thread race
                # QPixmapCache.remove(str(cache_key))
                # cache_.pop(f"filter_results__{str(cache_key)}", None)
                self.schedule_filter_task(annotation_id, filter_task, cache_key, ready_callback)
                return None
