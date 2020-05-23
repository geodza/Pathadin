from typing import Hashable, Callable

from filter_processor.filter_processor import FilterProcessor, F
from filter_processor.filter_processor_factory import FilterProcessorFactory
from filter.kmeans.kmeans_filter import kmeans_filter
from img.filter.kmeans_filter import KMeansFilterData, KMeansFilterResults
from slide_viewer.ui.common.model import AnnotationModel
from slide_viewer.ui.slide.widget.filter.region_data import build_region_data

F = KMeansFilterData
R = KMeansFilterResults


class KMeansFilterProcessorFactory(FilterProcessorFactory[F, R]):

	def create(self, filter_data: F) -> FilterProcessor[F, R]:
		if isinstance(filter_data, F):
			return KMeansFilterProcessor()


class KMeansFilterProcessor(FilterProcessor):

	def filter_task_key(self, filter_data: F, img_path: str, annotation: AnnotationModel) -> Hashable:
		rd = build_region_data(img_path, annotation, annotation.filter_level)
		return ('kmeans', img_path, rd, annotation.filter_level, filter_data.kmeans_params)

	def filter_task(self, filter_data: F, img_path: str, annotation: AnnotationModel) -> Callable[[], R]:
		return lambda: kmeans_filter(annotation, filter_data, img_path)
