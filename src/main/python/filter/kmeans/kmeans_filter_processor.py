from typing import Hashable, Callable

from annotation.model import AnnotationModel
from annotation_image.core import build_region_data
from filter.common.filter_model import FilterOutput
from filter.kmeans.kmeans_filter import kmeans_filter
from filter.kmeans.kmeans_filter_model import KMeansFilterData
from filter_processor.filter_processor import FilterProcessor, F
from filter_processor.filter_processor_factory import FilterProcessorFactory

F = KMeansFilterData


class KMeansFilterProcessorFactory(FilterProcessorFactory[F]):

	def create(self, filter_data: F) -> FilterProcessor[F]:
		if isinstance(filter_data, F):
			return KMeansFilterProcessor()


class KMeansFilterProcessor(FilterProcessor):

	def filter_task_key(self, filter_data: F, img_path: str, annotation: AnnotationModel) -> Hashable:
		rd = build_region_data(img_path, annotation, annotation.filter_level)
		return ('kmeans', img_path, rd, annotation.filter_level, filter_data.kmeans_params)

	def filter_task(self, filter_data: F, img_path: str, annotation: AnnotationModel) -> Callable[[], FilterOutput]:
		return lambda: kmeans_filter(annotation, filter_data, img_path)
