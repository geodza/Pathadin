from typing import Hashable, Callable

from filter.common.filter_output import FilterOutput
from filter_processor.filter_processor import FilterProcessor, F
from filter_processor.filter_processor_factory import FilterProcessorFactory
from filter.positive_pixel_count.positive_pixel_count_filter import positive_pixel_count_filter
from filter.positive_pixel_count.positive_pixel_count_filter_model import PositivePixelCountFilterData
from annotation.model import AnnotationModel
from annotation_image.core import build_region_data

F = PositivePixelCountFilterData


class PositivePixelCountFilterProcessorFactory(FilterProcessorFactory[F]):

	def create(self, filter_data: F) -> FilterProcessor[F]:
		if isinstance(filter_data, F):
			return PositivePixelCountFilterProcessor()


class PositivePixelCountFilterProcessor(FilterProcessor):

	def filter_task_key(self, filter_data: F, img_path: str, annotation: AnnotationModel) -> Hashable:
		rd = build_region_data(img_path, annotation, annotation.filter_level)
		return ('positive_pixel_count', img_path, rd, annotation.filter_level, filter_data.positive_pixel_count_params)

	def filter_task(self, filter_data: F, img_path: str, annotation: AnnotationModel) -> Callable[[], FilterOutput]:
		return lambda: positive_pixel_count_filter(annotation, filter_data, img_path)
