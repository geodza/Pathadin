from collections import defaultdict
from concurrent.futures import Future, ThreadPoolExecutor
from typing import Tuple, Optional, Callable, Union, List, Dict

from PyQt5.QtCore import QObject, pyqtSignal
from PyQt5.QtGui import QPixmapCache, QPixmap
from cachetools.keys import hashkey
from dataclasses import dataclass

from common.timeit_utils import timing
from common_image_qt.core import ndimg_to_bitmap
from common_qt.abcq_meta import ABCQMeta
from filter_processor.filter_processor import FilterProcessor
from img.filter.base_filter import FilterData, FilterResults2
from slide_viewer.cache_config import cache_lock, cache_key_func, pixmap_cache_lock, cache_, add_to_global_pending, \
	get_from_global_pending, \
	is_in_global_pending, remove_from_global_pending
from slide_viewer.ui.slide.widget.interface.annotation_pixmap_provider import AnnotationItemPixmapProvider
from slide_viewer.ui.slide.widget.interface.annotation_service import AnnotationService
from slide_viewer.ui.slide.widget.interface.filter_model_provider import FilterModelProvider
from slide_viewer.ui.slide.widget.interface.slide_path_provider import SlidePathProvider


# if __name__ == '__main__':
#     slide_path = r"D:\slide_cbir_47\temp\slides\slide-2019-09-19T18-08-52-R28-S3.mrxs"
#     ds = r"."
#     grid_length = 256
#     model_path = r"D:\Pathadin\src\main\python\256\unet_model_19_01_2020.h5"
#     rd = RegionData(slide_path, 0, (0, 0), ((41728, 63232), (42008, 63512)), AnnotationType.RECT)
#     fr = keras_model_filter(rd, KerasModelParams(model_path))
#     print(fr)

def not_canceled_done_callback(callback):
	def on_done(f: Future):
		if not f.cancelled():
			callback()

	return on_done


@dataclass
class AnnotationFilterProcessor(QObject, AnnotationItemPixmapProvider, metaclass=ABCQMeta):
	pool: ThreadPoolExecutor
	slide_path_provider: Union[SlidePathProvider, Callable[[], str]]
	annotation_service: AnnotationService
	filter_model_provider: Union[FilterModelProvider, Callable[[str], FilterData]]
	filterResultsChange = pyqtSignal(str, FilterResults2)
	filter_processor: FilterProcessor

	def __post_init__(self):
		QObject.__init__(self)
		# self.schedule_filter_task = debounce(0.5)(self.schedule_filter_task_to_pool)
		self.filterResultsChange.connect(self.on_filter_results_change)
		self.id = None  # debug purpose
		self.scheduled_or_running_tasks: Dict[str, List[Future]] = defaultdict(list)

	def on_filter_results_change(self, annotation_id: str, filter_results: FilterResults2) -> None:
		self.annotation_service.edit_filter_results(annotation_id, filter_results)

	def get_pixmap(self, annotation_id: str, ready_callback: Callable[[], None]) -> Optional[Tuple[int, QPixmap]]:
		annotation_model = self.annotation_service.get(annotation_id)
		if not annotation_model or annotation_model.filter_id is None:
			return None
		filter_id = annotation_model.filter_id
		filter_level = annotation_model.filter_level
		filter_data = self.filter_model_provider.get_filter_model(filter_id) if isinstance(self.filter_model_provider,
																						   FilterModelProvider) else self.filter_model_provider(
			filter_id)
		if filter_data is None:
			return None
		slide_path = self.slide_path_provider.get_slide_path() if isinstance(self.slide_path_provider,
																			 SlidePathProvider) else self.slide_path_provider()
		if slide_path is None:
			return None

		cache_key = hashkey(self.filter_processor.filter_task_key(filter_data, slide_path, annotation_model))
		with pixmap_cache_lock, cache_lock:
			pixmap = QPixmapCache.find(str(cache_key))
			# print(str(cache_key), pixmap)
			if pixmap:
				return filter_level, pixmap
			else:
				annotation_tasks = self.scheduled_or_running_tasks[annotation_id]
				# print(f"self.scheduled_or_running_tasks[{annotation_id}] size: {len(annotation_tasks)}")
				if is_in_global_pending(cache_key):
					t = get_from_global_pending(cache_key)
					if not t.cancelled() and not getattr(t, 'outdated', False):
						t.add_done_callback(not_canceled_done_callback(ready_callback))
				else:
					for t in annotation_tasks:
						setattr(t, 'outdated', True)
						if t.cancel():
							pass  # Successfully canceled scheduled but not started task.
						else:
							# Failed to cancel task because it already has started.
							# We cant kill it.
							# All we can do is to mark this task as "outdated" and then when task will finish we will ignore it results.
							pass
					filter_task = self.filter_processor.filter_task(filter_data, slide_path, annotation_model)
					new_task = self.pool.submit(filter_task)
					print("new_task submitted", cache_key)
					add_to_global_pending(cache_key, new_task)
					self.scheduled_or_running_tasks[annotation_id].append(new_task)

					def new_task_done(f):
						with pixmap_cache_lock, cache_lock:
							if not f.cancelled() and not getattr(f, 'outdated', False):
								try:
									filter_results: FilterResults2 = f.result()
									pixmap = timing(QPixmap.fromImage)(filter_results.img)
									if filter_results.bool_mask_ndimg is not None:
										bitmap = timing(ndimg_to_bitmap)(filter_results.bool_mask_ndimg)
										pixmap.setMask(bitmap)
									QPixmapCache.insert(str(cache_key), pixmap)
									cache_[cache_key] = filter_results
									self.filterResultsChange.emit(annotation_id, filter_results)
									# self.annotation_service.edit_filter_results(annotation_id, filter_results)
									ready_callback()
								except Exception as e:
									# QMessageBox.critical(None,"Error in filters", str(e))
									raise e
							self.scheduled_or_running_tasks[annotation_id].remove(new_task)
							remove_from_global_pending(cache_key)

					new_task.add_done_callback(new_task_done)
				return None
