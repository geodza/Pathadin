from typing import Hashable, Callable

from filter.nuclei.nuclei_filter import nuclei_filter
from filter_processor.filter_processor import FilterProcessor, F
from filter_processor.filter_processor_factory import FilterProcessorFactory
from img.filter.nuclei import NucleiFilterData, NucleiFilterResults
from slide_viewer.ui.common.model import AnnotationModel
from slide_viewer.ui.slide.widget.filter.region_data import build_region_data

F = NucleiFilterData
R = NucleiFilterResults


class NucleiFilterProcessorFactory(FilterProcessorFactory[F, R]):

	def create(self, filter_data: F) -> FilterProcessor[F, R]:
		if isinstance(filter_data, F):
			return NucleiFilterProcessor()


class NucleiFilterProcessor(FilterProcessor):

	def filter_task_key(self, filter_data: F, img_path: str, annotation: AnnotationModel) -> Hashable:
		rd = build_region_data(img_path, annotation, annotation.filter_level)
		return ('nuclei', img_path, rd, annotation.filter_level, filter_data.nuclei_params)

	def filter_task(self, filter_data: F, img_path: str, annotation: AnnotationModel) -> Callable[[], R]:
		return lambda: nuclei_filter(annotation, filter_data, img_path)
