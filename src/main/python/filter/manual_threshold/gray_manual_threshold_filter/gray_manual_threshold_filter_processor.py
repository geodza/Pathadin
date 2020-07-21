from typing import Hashable, Callable

from annotation.model import AnnotationModel
from annotation_image.core import build_region_data
from filter.common.filter_output import FilterOutput
from filter.manual_threshold.manual_threshold_filter import gray_manual_threshold_filter
from filter.manual_threshold.manual_threshold_filter_model import GrayManualThresholdFilterData
from filter_processor.filter_processor import FilterProcessor, F
from filter_processor.filter_processor_factory import FilterProcessorFactory

F = GrayManualThresholdFilterData


class GrayManualThresholdFilterProcessorFactory(FilterProcessorFactory[F]):

	def create(self, filter_data: F) -> FilterProcessor[F]:
		if isinstance(filter_data, F):
			return GrayManualThresholdFilterProcessor()


class GrayManualThresholdFilterProcessor(FilterProcessor):

	def filter_task_key(self, filter_data: F, img_path: str, annotation: AnnotationModel) -> Hashable:
		rd = build_region_data(img_path, annotation, annotation.filter_level)
		return ('gray', img_path, rd, annotation.filter_level, filter_data.gray_range)

	def filter_task(self, filter_data: F, img_path: str, annotation: AnnotationModel) -> Callable[[], FilterOutput]:
		return lambda: gray_manual_threshold_filter(annotation, filter_data, img_path)
