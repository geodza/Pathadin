from abc import ABC, abstractmethod
from typing import List, TypeVar, Generic, Hashable, Callable

from img.filter.base_filter import FilterResults2
from slide_viewer.ui.common.model import AnnotationModel

F = TypeVar('F')
R = TypeVar('R', bound=FilterResults2)
G = TypeVar('G')


class FilterProcessor(ABC, Generic[F, R]):

	# def filter_batch(self, filter_data: F, img_path: str, annotations: List[AnnotationModel]) -> List[R]:
	# 	# consider caching, multithreading, yielding, client-server, calling another process
	# 	# batch is for possibly heavy operations like loading keras model or some filter-specific optimizations.
	# 	rr = []
	# 	for a in annotations:
	# 		task = self.filter_task(filter_data, img_path, a)
	# 		r = task()
	# 		rr.append(r)
	# 	return rr

	@abstractmethod
	def filter_task(self, filter_data: F, img_path: str, annotation: AnnotationModel) -> Callable[[], R]:
		pass

	@abstractmethod
	def filter_task_key(self, filter_data: F, img_path: str, annotation: AnnotationModel) -> Hashable:
		pass

# @abstractmethod
# def filter_task_arg(self, annotation: AnnotationModel, filter_data: F, img_path: str) -> G:
# 	pass
