from typing import List, Any, Hashable

from dataclasses import field, dataclass

from filter_processor.filter_processor import FilterProcessor
from filter_processor.filter_processor_factory import FilterProcessorFactory
from annotation.model import AnnotationModel

F = Any
R = Any
G = Any


@dataclass
class CompositeFilterProcessor(FilterProcessor):
	factories: List[FilterProcessorFactory] = field(default_factory=list)

	def find_delegate(self, filter_data: F) -> FilterProcessor[F]:
		for f in self.factories:
			d = f.create(filter_data)
			if d is not None:
				return d
		raise ValueError(f"CompositeFilterProcessor. No appropriate delegate found for {filter_data} in {self.factories}")

	def filter_task(self, filter_data: F, img_path: str, annotation: AnnotationModel) -> R:
		return self.find_delegate(filter_data).filter_task(filter_data, img_path, annotation)

	def filter_task_key(self, filter_data: F, img_path: str, annotation: AnnotationModel) -> Hashable:
		return self.find_delegate(filter_data).filter_task_key(filter_data, img_path, annotation)
