from typing import Hashable, Callable

from filter.common.filter_output import FilterOutput
from filter.nuclei.nuclei_filter import nuclei_filter
from filter_processor.filter_processor import FilterProcessor, F
from filter_processor.filter_processor_factory import FilterProcessorFactory
from filter.nuclei.nuclei_filter_model import NucleiFilterData
from annotation.model import AnnotationModel
from annotation_image.core import build_region_data

F = NucleiFilterData

class NucleiFilterProcessorFactory(FilterProcessorFactory[F]):

	def create(self, filter_data: F) -> FilterProcessor[F]:
		if isinstance(filter_data, F):
			return NucleiFilterProcessor()


class NucleiFilterProcessor(FilterProcessor):

	def filter_task_key(self, filter_data: F, img_path: str, annotation: AnnotationModel) -> Hashable:
		rd = build_region_data(img_path, annotation, annotation.filter_level)
		return ('nuclei', img_path, rd, annotation.filter_level, filter_data.nuclei_params)

	def filter_task(self, filter_data: F, img_path: str, annotation: AnnotationModel) -> Callable[[], FilterOutput]:
		return lambda: nuclei_filter(annotation, filter_data, img_path)
