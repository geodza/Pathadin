from concurrent.futures import Future, ThreadPoolExecutor
from typing import Tuple, Optional, Callable, Union, cast

import cv2
import numpy as np
import openslide
import skimage
import skimage.color
import skimage.measure
from PyQt5.QtCore import QObject, pyqtSignal
from PyQt5.QtGui import QPixmapCache, QPixmap, QPolygon
from cachetools.keys import hashkey
from dataclasses import dataclass, asdict
from shapely.affinity import translate
from shapely.geometry import box

from common.debounce import debounce
from common.dict_utils import remove_none_values
from common.grid_utils import pos_range
from common.points_utils import deshift_points, rescale_points
from common_htk.nuclei import ndimg_to_nuclei_seg_mask
from common_image.core.hist import ndimg_to_hist
from common_image.core.hist_html import build_histogram_html
from common_image.core.img_polygon_utils import create_polygon_image
from common_image.core.kmeans import ndimg_to_quantized_ndimg
from common_image.core.mode_convert import convert_ndimg
from common_image.core.object_convert import pilimg_to_ndimg
from common_image.core.resize import resize_ndimg, resize_ndarray
from common_image.core.skimage_threshold import find_ndimg_skimage_threshold
from common_image.core.threshold import ndimg_to_thresholded_ndimg
from common_image.model.ndimg import Ndimg
from common_image_qt.core import ndimg_to_qimg, ndimg_to_bitmap
from common_qt.abcq_meta import ABCQMeta
from common_qt.util.qobjects_convert_util import ituple_to_qpoint
from common_shapely.shapely_utils import get_polygon_bbox_size, scale_at_origin, locate, get_polygon_bbox_pos
from img.filter.base_filter import FilterData, FilterResults2
from img.filter.keras_model import KerasModelFilterResults, KerasModelFilterData, KerasModelParams
from img.filter.kmeans_filter import KMeansFilterData, KMeansFilterResults, KMeansParams
from img.filter.manual_threshold import ManualThresholdFilterData, HSVManualThresholdFilterData, \
    GrayManualThresholdFilterData
from img.filter.nuclei import NucleiFilterData, NucleiFilterResults, NucleiParams
from img.filter.positive_pixel_count import PositivePixelCountFilterResults, PositivePixelCountFilterData, PositivePixelCountParams, \
    positive_pixel_count2
from img.filter.skimage_threshold import SkimageAutoThresholdFilterData, SkimageThresholdParams, \
    SkimageMinimumThresholdFilterData, SkimageMeanThresholdFilterData
from img.filter.threshold_filter import ThresholdFilterResults
from img.proc.mask import build_mask
from img.proc.region import RegionData, read_region
from slice.annotation_shapely_utils import annotation_geom_to_shapely_geom
from slice.image_shapely_utils import get_slide_polygon_bbox_rgb_region
from slide_viewer.cache_config import cache_lock, cache_key_func, pixmap_cache_lock, cache_, gcached, add_to_global_pending, get_from_global_pending, \
    is_in_global_pending, remove_from_global_pending, closure_nonhashable
from slide_viewer.common.slide_helper import SlideHelper
from slide_viewer.ui.common.model import AnnotationModel, AnnotationGeometry
from slide_viewer.ui.slide.widget.interface.annotation_pixmap_provider import AnnotationItemPixmapProvider
from slide_viewer.ui.slide.widget.interface.annotation_service import AnnotationService
from slide_viewer.ui.slide.widget.interface.filter_model_provider import FilterModelProvider
from slide_viewer.ui.slide.widget.interface.slide_path_provider import SlidePathProvider


def build_region_data(slide_path: str, model: AnnotationModel, filter_level: int) -> RegionData:
    origin_point = model.geometry.origin_point
    points = tuple(model.geometry.points)
    return RegionData(slide_path, filter_level, origin_point, points, model.geometry.annotation_type)


def read_masked_region(rd: RegionData) -> Ndimg:
    pilimg = read_region(rd)
    level0_qsize = QPolygon([ituple_to_qpoint(p) for p in rd.points]).boundingRect().size()
    sx, sy = pilimg.width / level0_qsize.width(), pilimg.height / level0_qsize.height()
    ndimg = pilimg_to_ndimg(pilimg)
    points = deshift_points(rd.points, rd.origin_point)
    points = rescale_points(points, sx, sy)
    # ituples = ituples_to_polygon_ituples(rd.points)
    mask = build_mask(ndimg.ndarray.shape, points, rd.annotation_type, background_color=0, color=255)
    # (0,0,0,0) for rgba means transparent
    masked_ndimg = cv2.bitwise_and(ndimg.ndarray, ndimg.ndarray, mask=mask)
    # ndimg.ndimg = mask_ndimg(ndimg.ndimg, points, rd.annotation_type)
    ndimg.ndarray = masked_ndimg
    # mask = cv2.bitwise_not(mask)
    ndimg.bool_mask_ndarray = mask != 0
    return ndimg


@gcached
def kmeans_filter(rd: RegionData, params: KMeansParams) -> KMeansFilterResults:
    ndimg = read_masked_region(rd)
    # img_to_kmeans_quantized_img_ = closure_nonhashable(hashkey(rd), ndimg, img_to_kmeans_quantized_img)
    kwargs = remove_none_values(asdict(params))
    kwargs['init'] = params.init.value
    quantized_ndimg = ndimg_to_quantized_ndimg(ndimg, **kwargs)
    # quantized_ndimg = img_to_kmeans_quantized_img_(params)
    hist = ndimg_to_hist(quantized_ndimg)
    hist_html = build_histogram_html(hist.sorted_most_freq_colors, hist.sorted_most_freq_colors_counts)
    qimg = ndimg_to_qimg(quantized_ndimg)
    res = KMeansFilterResults(qimg, ndimg.bool_mask_ndarray, hist_html)
    return res


@gcached
def nuclei_filter(rd: RegionData, params: NucleiParams) -> NucleiFilterResults:
    ndimg = read_masked_region(rd)
    seg_mask = ndimg_to_nuclei_seg_mask(ndimg, params)
    region_props = skimage.measure.regionprops(seg_mask.ndarray)
    labeled_ndimg = skimage.color.label2rgb(seg_mask.ndarray, ndimg.ndarray, bg_label=0)
    labeled_ndimg = skimage.util.img_as_ubyte(labeled_ndimg, force_copy=True)
    qimg = ndimg_to_qimg(Ndimg(labeled_ndimg, "RGB", ndimg.bool_mask_ndarray))
    return NucleiFilterResults(qimg, ndimg.bool_mask_ndarray, len(region_props))


# @gcached
def load_keras_model(model_path: str):
    from tensorflow.python.keras.saving import load_model
    keras_model = load_model(model_path)
    return keras_model


@gcached
def keras_model_filter(rd: RegionData, params: KerasModelParams) -> KerasModelFilterResults:
    keras_model = load_keras_model(params.model_path)
    input_shape = keras_model.input_shape[1:]
    input_size = input_shape[:2]
    # TODO get from KerasModelParams
    input_scale = 1
    rescale_source_patch = True
    polygon0 = annotation_geom_to_shapely_geom(AnnotationGeometry(annotation_type=rd.annotation_type, origin_point=rd.origin_point, points=rd.points))
    polygon_size0 = get_polygon_bbox_size(polygon0)

    input_size0 = (input_size[0] * input_scale, input_size[1] * input_scale)

    sh = SlideHelper(rd.img_path)
    level = rd.level
    if level is None or level == '':
        level = min(2, sh.level_count - 1)

    level = int(level)
    level_downsample = sh.level_downsamples[level]
    level_scale = 1 / level_downsample
    filter_image_size = get_polygon_bbox_size(polygon0, level_scale)

    # filter_image = np.empty((*filter_image_size, 3), dtype='uint8')
    filter_image = np.zeros((*filter_image_size, 4), dtype='uint8')

    # nrows, ncols = get_polygon_bbox_size(polygon0, level_scale)
    def convert_image(ndarray: np.ndarray) -> np.ndarray:
        return np.atleast_3d(np.squeeze(ndarray / 255)).astype(np.float32)

    # height0, width0 = get_polygon_bbox_size(polygon0)
    p0 = get_polygon_bbox_pos(polygon0)
    with openslide.open_slide(rd.img_path) as slide:
        for x0, y0 in pos_range((polygon_size0[1], polygon_size0[0]), input_size0[1], input_size0[0]):
            patch0 = box(x0, y0, x0 + input_size0[1], y0 + input_size0[0])
            patch0 = translate(patch0, p0[0], p0[1])
            patch_image = get_slide_polygon_bbox_rgb_region(slide, patch0, level, rescale_result_image=False)
            patch_image_shape = patch_image.ndarray.shape
            if patch_image_shape[:2] != input_size:
                patch_image = resize_ndimg(patch_image, input_size)
            patch_ndarray = convert_image(patch_image.ndarray)
            patch_images_batch = np.array([patch_ndarray])
            patch_labels_batch = keras_model.predict(patch_images_batch)
            patch_label = patch_labels_batch[0]
            # tile_mask = tile_mask>=0.5
            # tile_mask = tile_mask/2
            # io.imshow(np.squeeze(patch_ndarray))
            # io.show()
            # io.imshow(np.squeeze(patch_label))
            # io.show()
            x, y = int(x0 * level_scale), int(y0 * level_scale)
            nrows, ncols = (int(input_size[0] * level_scale), int(input_size[1] * level_scale))
            if patch_label.shape[:2] != (nrows, ncols):
                patch_label_ = resize_ndarray(patch_label, (nrows, ncols))
            patch_label_ = skimage.util.invert(patch_label_) if params.invert else patch_label_
            patch_label_ *= params.alpha_scale
            patch_label_ = skimage.util.img_as_ubyte(patch_label_)
            patch_label_ = patch_label_.reshape(patch_label_.shape[:2])
            nrows, ncols = min(nrows, filter_image[y:, ...].shape[0]), min(ncols, filter_image[y:, x:, ...].shape[1])
            filter_image[y:y + nrows, x:x + ncols, 3] = patch_label_[:nrows, :ncols]

    # mask_color = np.array([0, 255, 0, 0], dtype='uint8')
    # region_mask_rgba = np.tile(mask_color, region_mask.shape)
    # region_mask_rgba[..., 3] = np.squeeze(region_mask)
    filter_image[..., 1] = 255
    # io.imshow(np.squeeze(filter_image))
    # io.show()
    polygon_ = scale_at_origin(locate(polygon0, polygon0), level_scale)
    bool_mask_ndarray = create_polygon_image(polygon_, 'L', 255, create_mask=False).ndarray
    qimg = ndimg_to_qimg(Ndimg(filter_image, "RGBA", bool_mask_ndarray))
    return KerasModelFilterResults(qimg, bool_mask_ndarray)


# if __name__ == '__main__':
#     slide_path = r"D:\slide_cbir_47\temp\slides\slide-2019-09-19T18-08-52-R28-S3.mrxs"
#     ds = r"."
#     grid_length = 256
#     model_path = r"D:\Pathadin\src\main\python\256\unet_model_19_01_2020.h5"
#     rd = RegionData(slide_path, 0, (0, 0), ((41728, 63232), (42008, 63512)), AnnotationType.RECT)
#     fr = keras_model_filter(rd, KerasModelParams(model_path))
#     print(fr)


def threshold_filter(img: Ndimg, threshold_range: tuple) -> ThresholdFilterResults:
    thresholded_ndimg = ndimg_to_thresholded_ndimg(img, threshold_range)
    hist = ndimg_to_hist(thresholded_ndimg)
    hist_html = build_histogram_html(hist.sorted_most_freq_colors, hist.sorted_most_freq_colors_counts)
    qimg = ndimg_to_qimg(thresholded_ndimg)
    res = ThresholdFilterResults(qimg, thresholded_ndimg.bool_mask_ndarray, hist_html)
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
    kwargs = remove_none_values(asdict(params.params)) if params.params else {}
    # return ndimg_to_skimage_thresholded_ndimg(img.ndarray, params.type.name, **kwargs)
    threshold = find_ndimg_skimage_threshold(converted_ndimg, params.type.name, **kwargs)
    threshold_range = (0, threshold)
    # threshold_range = ndimg_to_skimage_threshold_range(params, converted_ndimg)
    return threshold_filter(converted_ndimg, threshold_range)


@gcached
def positive_pixel_count_filter(rd: RegionData, params: PositivePixelCountParams):
    ndimg = read_masked_region(rd)
    converted_ndimg = closure_nonhashable(hashkey(rd), ndimg, convert_ndimg)("RGB")
    ndimg, stats = positive_pixel_count2(converted_ndimg, params)
    qimg = ndimg_to_qimg(ndimg)
    res = PositivePixelCountFilterResults(qimg, ndimg.bool_mask_ndarray, stats)
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
