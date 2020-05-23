from typing import Hashable, Callable

from filter_processor.filter_processor import FilterProcessor, F
from filter_processor.filter_processor_factory import FilterProcessorFactory
from filter.keras.keras_model_filter import keras_model_filter
from img.filter.keras_model import KerasModelFilterData, KerasModelFilterResults
from slide_viewer.ui.common.model import AnnotationModel
from slide_viewer.ui.slide.widget.filter.region_data import build_region_data

F = KerasModelFilterData
R = KerasModelFilterResults


class KerasModelFilterProcessorFactory(FilterProcessorFactory[F, R]):

	def create(self, filter_data: F) -> FilterProcessor[F, R]:
		if isinstance(filter_data, F):
			return KerasModelFilterProcessor()


class KerasModelFilterProcessor(FilterProcessor):

	def filter_task_key(self, filter_data: F, img_path: str, annotation: AnnotationModel) -> Hashable:
		rd = build_region_data(img_path, annotation, annotation.filter_level)
		return ('keras_model', img_path, rd, annotation.filter_level, filter_data.keras_model_params)

	def filter_task(self, filter_data: F, img_path: str, annotation: AnnotationModel) -> Callable[[], R]:
		return lambda: keras_model_filter(annotation, filter_data, img_path)
