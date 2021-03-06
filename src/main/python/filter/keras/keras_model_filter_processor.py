from typing import Hashable, Callable

from filter.common.filter_output import FilterOutput
from filter_processor.filter_processor import FilterProcessor, F
from filter_processor.filter_processor_factory import FilterProcessorFactory
from filter.keras.keras_model_filter import keras_model_filter
from filter.keras.keras_model_filter_model import KerasModelFilterData
from annotation.model import AnnotationModel
from annotation_image.core import build_region_data

F = KerasModelFilterData


class KerasModelFilterProcessorFactory(FilterProcessorFactory[F]):

	def create(self, filter_data: F) -> FilterProcessor[F]:
		if isinstance(filter_data, F):
			return KerasModelFilterProcessor()


class KerasModelFilterProcessor(FilterProcessor):

	def filter_task_key(self, filter_data: F, img_path: str, annotation: AnnotationModel) -> Hashable:
		rd = build_region_data(img_path, annotation, annotation.filter_level)
		return ('keras_model', img_path, rd, annotation.filter_level, filter_data.keras_model_params)

	def filter_task(self, filter_data: F, img_path: str, annotation: AnnotationModel) -> Callable[[], FilterOutput]:
		return lambda: keras_model_filter(annotation, filter_data, img_path)
