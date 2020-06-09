from typing import Hashable, Callable

from annotation.model import AnnotationModel
from annotation_image.core import build_region_data
from filter.common.filter_model import FilterOutput
from filter.skimage_threshold.skimage_threshold_filter import skimage_threshold_filter
from filter.skimage_threshold.skimage_threshold_filter_model import SkimageThresholdFilterData, \
	SkimageMeanThresholdFilterData, \
	SkimageMinimumThresholdFilterData
from filter_processor.filter_processor import FilterProcessor, F
from filter_processor.filter_processor_factory import FilterProcessorFactory

F = SkimageThresholdFilterData


class SkimageThresholdFilterProcessorFactory(FilterProcessorFactory[F]):

	def create(self, filter_data: F) -> FilterProcessor[F]:
		if isinstance(filter_data, F):
			return SkimageThresholdFilterProcessor()


class SkimageThresholdFilterProcessor(FilterProcessor):

	def filter_task_key(self, filter_data: F, img_path: str, annotation: AnnotationModel) -> Hashable:
		rd = build_region_data(img_path, annotation, annotation.filter_level)
		if isinstance(filter_data, SkimageMeanThresholdFilterData):
			return ('skimage_mean', img_path, rd, annotation.filter_level)
		elif isinstance(filter_data, SkimageMinimumThresholdFilterData):
			return (
			'skimage_minimum', img_path, rd, annotation.filter_level, filter_data.skimage_threshold_minimum_params)
		else:
			raise ValueError()

	def filter_task(self, filter_data: F, img_path: str, annotation: AnnotationModel) -> Callable[[], FilterOutput]:
		return lambda: skimage_threshold_filter(annotation, filter_data, img_path)
