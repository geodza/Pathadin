from typing import Hashable, Callable

from filter_processor.filter_processor import FilterProcessor, F
from filter_processor.filter_processor_factory import FilterProcessorFactory
from filter.positive_pixel_count.positive_pixel_count_filter import positive_pixel_count_filter
from img.filter.positive_pixel_count import PositivePixelCountFilterData, PositivePixelCountFilterResults
from slide_viewer.ui.common.model import AnnotationModel
from slide_viewer.ui.slide.widget.filter.region_data import build_region_data

F = PositivePixelCountFilterData
R = PositivePixelCountFilterResults


class PositivePixelCountFilterProcessorFactory(FilterProcessorFactory[F, R]):

	def create(self, filter_data: F) -> FilterProcessor[F, R]:
		if isinstance(filter_data, F):
			return PositivePixelCountFilterProcessor()


class PositivePixelCountFilterProcessor(FilterProcessor):

	def filter_task_key(self, filter_data: F, img_path: str, annotation: AnnotationModel) -> Hashable:
		rd = build_region_data(img_path, annotation, annotation.filter_level)
		return ('positive_pixel_count', img_path, rd, annotation.filter_level, filter_data.positive_pixel_count_params)

	def filter_task(self, filter_data: F, img_path: str, annotation: AnnotationModel) -> Callable[[], R]:
		return lambda: positive_pixel_count_filter(annotation, filter_data, img_path)
