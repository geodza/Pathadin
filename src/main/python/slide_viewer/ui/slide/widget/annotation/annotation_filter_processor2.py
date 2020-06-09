from collections import defaultdict
from concurrent.futures import Future, ThreadPoolExecutor
from typing import Tuple, Optional, Callable, Union, List, Dict

from PyQt5.QtGui import QPixmapCache, QPixmap
from cachetools.keys import hashkey
from dataclasses import dataclass

from annotation.model import AnnotationModel
from common.concurrent_utils import not_canceled_done_callback
from common.timeit_utils import timing
from common_image_qt.core import ndimg_to_bitmap
from filter.common.filter_model import FilterOutput
from filter_processor.filter_processor import FilterProcessor
from slide_viewer.cache_config import cache_lock, add_to_global_pending, \
	get_from_global_pending, \
	is_in_global_pending, remove_from_global_pending
from slide_viewer.ui.slide.widget.annotation.annotation_service import AnnotationService
from slide_viewer.ui.slide.widget.filter.filter_data_service import FilterDataService
from slide_viewer.ui.slide.widget.interface.annotation_pixmap_provider import AnnotationItemPixmapProvider
from slide_viewer.ui.slide.widget.interface.slide_path_provider import SlidePathProvider


@dataclass
class AnnotationFilterProcessor2():
	pool: ThreadPoolExecutor
	slide_path_provider: Union[SlidePathProvider, Callable[[], str]]
	annotation_service: AnnotationService
	filter_data_service: FilterDataService
	filter_processor: FilterProcessor

	def __post_init__(self):
		self.id = None  # debug purpose
		self.scheduled_or_running_tasks: Dict[str, List[Future]] = defaultdict(list)

	def task_key(self, annotation_id:str)->Optional[str]:
		annotation_model = self.annotation_service.get(annotation_id)
		if not annotation_model or annotation_model.filter_id is None:
			return None
		annotation_model = annotation_model.copy(deep=True)
		filter_id = annotation_model.filter_id
		filter_level = annotation_model.filter_level
		filter_data = self.filter_data_service.get_filter_item(filter_id)
		if filter_data is None:
			return None
		slide_path = self.slide_path_provider.get_slide_path() if isinstance(self.slide_path_provider,
																			 SlidePathProvider) else self.slide_path_provider()
		if slide_path is None:
			return None

		cache_key = hashkey(self.filter_processor.filter_task_key(filter_data, slide_path, annotation_model))
		return cache_key

	def process_task(self, annotation_model:AnnotationModel, ):
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
				with cache_lock:
					if not f.cancelled() and not getattr(f, 'outdated', False):
						try:
							filter_output: FilterOutput = f.result()
							pixmap = timing(QPixmap.fromImage)(filter_output.img)
							if filter_output.bool_mask_ndimg is not None:
								bitmap = timing(ndimg_to_bitmap)(filter_output.bool_mask_ndimg)
								pixmap.setMask(bitmap)
							QPixmapCache.insert(str(cache_key), pixmap)
							self.annotation_service.edit_filter_results(annotation_id, filter_output.results)
							ready_callback()
						except Exception as e:
							# QMessageBox.critical(None,"Error in filters", str(e))
							raise e
					self.scheduled_or_running_tasks[annotation_id].remove(new_task)
					remove_from_global_pending(cache_key)

			new_task.add_done_callback(new_task_done)
		return None
