from collections import OrderedDict
from concurrent.futures import Future, ThreadPoolExecutor
from typing import Set, Tuple, Optional, Callable, Union

from PyQt5.QtCore import QObject, pyqtSignal
from PyQt5.QtGui import QPixmapCache, QPixmap, QPolygon
from dataclasses import dataclass, field

from slide_viewer.cache_config import cache_lock, cache_key_func, pixmap_cache_lock, cache_
from slide_viewer.common.debounce import debounce
from slide_viewer.common_qt.abcq_meta import ABCQMeta
from slide_viewer.common_qt.qobjects_convert_util import tuples_to_qpoints, qpoints_to_tuples
from slide_viewer.filter.filter_processing import qimage_result_
from slide_viewer.ui.model.annotation_type import AnnotationType
from slide_viewer.ui.model.filter.base_filter import FilterData, FilterResults
from slide_viewer.ui.model.filter.region_data import RegionData
from slide_viewer.ui.odict.deep.model import AnnotationModel
from slide_viewer.ui.slide.widget.interface.annotation_model_provider import AnnotationModelProvider
from slide_viewer.ui.slide.widget.interface.annotation_pixmap_provider import AnnotationItemPixmapProvider
from slide_viewer.ui.slide.widget.interface.filter_model_provider import FilterModelProvider
from slide_viewer.ui.slide.widget.interface.slide_path_provider import SlidePathProvider


def build_region_data(slide_path: str, model: AnnotationModel, filter_level: int) -> RegionData:
    if model.geometry.annotation_type in (AnnotationType.RECT, AnnotationType.ELLIPSE, AnnotationType.LINE):
        # p1, p2 = model.geometry.points
        rect_polygon = QPolygon(QPolygon(tuples_to_qpoints(model.geometry.points)).boundingRect(), True)
        qpoints = tuple(rect_polygon)
        points = tuple(qpoints_to_tuples(qpoints))
    else:
        points = tuple(model.geometry.points)

    origin_point = model.geometry.origin_point
    return RegionData(slide_path, filter_level, origin_point, points)


@dataclass
class AnnotationFilterProcessor(QObject, AnnotationItemPixmapProvider, metaclass=ABCQMeta):
    pool: ThreadPoolExecutor
    slide_path_provider: Union[SlidePathProvider, Callable[[], str]]
    annotation_model_provider: Union[AnnotationModelProvider, Callable[[str], AnnotationModel]]
    filter_model_provider: Union[FilterModelProvider, Callable[[str], FilterData]]
    pending: Set = field(default_factory=set)
    filterResultsChange = pyqtSignal(str, FilterResults)

    def __post_init__(self):
        QObject.__init__(self)

    def task(self, annotation_id: str, data: Tuple[RegionData, Optional[str], FilterData],
             ready_callback):
        filter_results = qimage_result_(*data)
        # filter_results = build_filter_results(data, result_img)
        with cache_lock:
            if self:
                self.filterResultsChange.emit(annotation_id, filter_results)
                self.pending.remove(data)
                ready_callback()

    @debounce(0.05)
    def schedule_pixmap(self, annotation_id: str,
                        data: Tuple[RegionData, Optional[str], FilterData], ready_callback):
        with cache_lock:
            if data not in self.pending:
                self.pending.add(data)
                future = self.pool.submit(self.task, annotation_id, data, ready_callback)

                def done_func(ff: Future):
                    try:
                        ff.result()
                    except Exception as e:
                        raise e

                future.add_done_callback(done_func)

    def get_pixmap(self, annotation_id: str, ready_callback) -> Optional[Tuple[int, QPixmap]]:
        annotation_model = self.annotation_model_provider.get_annotation_model(annotation_id) if isinstance(
            self.annotation_model_provider, AnnotationModelProvider) else self.annotation_model_provider(annotation_id)
        if annotation_model.filter_id is None:
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
        data = (region_data, None, filter_data)
        cache_key = cache_key_func('qimage_result_')(*data)
        with pixmap_cache_lock:
            pixmap = QPixmapCache.find(str(cache_key))
            if pixmap is not None:
                return filter_level, pixmap
            else:
                with cache_lock:
                    if cache_key in cache_:
                        fr: FilterResults = cache_.get(cache_key)
                        pixmap = QPixmap.fromImage(fr.img)
                        QPixmapCache.insert(str(cache_key), pixmap)
                        return filter_level, pixmap
                    else:
                        self.schedule_pixmap(annotation_id, data, ready_callback)
                        return None
