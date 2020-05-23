from typing import Hashable, Callable

from filter.manual_threshold.manual_threshold_filter import hsv_manual_threshold_filter
from filter_processor.filter_processor import FilterProcessor, F
from filter_processor.filter_processor_factory import FilterProcessorFactory
from img.filter.manual_threshold import HSVManualThresholdFilterData
from img.filter.threshold_filter import ThresholdFilterResults
from slide_viewer.ui.common.model import AnnotationModel
from slide_viewer.ui.slide.widget.filter.region_data import build_region_data

F = HSVManualThresholdFilterData
R = ThresholdFilterResults


class HSVManualThresholdFilterProcessorFactory(FilterProcessorFactory[F, R]):

	def create(self, filter_data: F) -> FilterProcessor[F, R]:
		if isinstance(filter_data, F):
			return HSVManualThresholdFilterProcessor()


class HSVManualThresholdFilterProcessor(FilterProcessor):

	def filter_task_key(self, filter_data: F, img_path: str, annotation: AnnotationModel) -> Hashable:
		rd = build_region_data(img_path, annotation, annotation.filter_level)
		return ('hsv', img_path, rd, annotation.filter_level, filter_data.hsv_range)

	def filter_task(self, filter_data: F, img_path: str, annotation: AnnotationModel) -> Callable[[], R]:
		return lambda: hsv_manual_threshold_filter(annotation, filter_data, img_path)
