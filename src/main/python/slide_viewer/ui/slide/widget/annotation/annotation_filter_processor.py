from collections import defaultdict
from concurrent.futures import Future, ThreadPoolExecutor
from threading import Lock
from typing import Tuple, Optional, Callable, Union, Dict, Iterable

from PyQt5.QtCore import QObject, pyqtSignal
from PyQt5.QtGui import QPixmapCache, QPixmap
from cachetools.keys import hashkey
from dataclasses import dataclass

from common.timeit_utils import timing
from common_image_qt.core import ndimg_to_bitmap
from filter.common.filter_output import FilterOutput
from filter_processor.filter_processor import FilterProcessor
from slide_viewer.cache_config import cache_
from slide_viewer.ui.slide.widget.annotation.annotation_service import AnnotationService
from slide_viewer.ui.slide.widget.filter.filter_data_service import FilterDataService
from slide_viewer.ui.slide.widget.interface.annotation_pixmap_provider import AnnotationItemPixmapProvider
from slide_viewer.ui.slide.widget.interface.slide_path_provider import SlidePathProvider


class FilterFutureSignals(QObject):
	result = pyqtSignal(str, str, FilterOutput, object)


# @dataclass
# class FilterFutureData:
# 	is_outdated: bool = False
# 	signals: FilterFutureSignals = field(default_factory=FilterFutureSignals)

def add_task_success_callback(task: Future, callback) -> None:
	# print("add_task_success_callback", callback)
	if hasattr(task, 'filter_future_success_callbacks'):
		getattr(task, 'filter_future_success_callbacks').append(callback)
	else:
		setattr(task, 'filter_future_success_callbacks', [callback])


def get_task_success_callbacks(task: Future) -> Iterable[Callable]:
	return getattr(task, 'filter_future_success_callbacks')


def get_task_filter_future_signals(task: Future) -> FilterFutureSignals:
	return getattr(task, 'filter_future_signals')


def set_task_filter_future_signals(task: Future, filter_future_signals: FilterFutureSignals) -> None:
	setattr(task, 'filter_future_signals', filter_future_signals)


def is_task_outdated(task: Future) -> bool:
	return getattr(task, 'outdated', False)


def mark_task_outdated(task: Future) -> None:
	setattr(task, 'outdated', True)


def build_task_callback(annotation_id: str, cache_key: str) -> Callable[
	[Future], None]:
	def new_task_done(future: Future):
		if not future.cancelled() and not is_task_outdated(future):
			try:
				filter_output: FilterOutput = future.result()
				success_callbacks = get_task_success_callbacks(future)
				get_task_filter_future_signals(future).result.emit(annotation_id, cache_key, filter_output,
																   success_callbacks)
			except Exception as e:
				raise e

	return new_task_done


@dataclass
class AnnotationFilterProcessor(AnnotationItemPixmapProvider):
	pool: ThreadPoolExecutor
	slide_path_provider: Union[SlidePathProvider, Callable[[], str]]
	annotation_service: AnnotationService
	filter_data_service: FilterDataService
	filter_processor: FilterProcessor

	# filter_processor2: AnnotationFilterProcessor2

	def __post_init__(self):
		self.id = None  # debug purpose
		self.scheduled_or_running_tasks: Dict[str, Dict[str, Future]] = defaultdict(defaultdict)
		self.scheduled_or_running_tasks_lock: Lock = Lock()

	def get_pixmap(self, annotation_id: str, ready_callback: Callable[[], None]) -> Optional[Tuple[int, QPixmap]]:
		annotation_model = self.annotation_service.get(annotation_id)
		# We take snapshot of annotation model because it can be edited during this call.
		# If we suppose that annotation_model can be edited only in main gui-thread, then this snapshot is unnecessary.
		# annotation_model = annotation_model.copy(deep=True)
		if not annotation_model or annotation_model.filter_id is None:
			return None
		filter_id = annotation_model.filter_id
		filter_level = annotation_model.filter_level
		filter_data = self.filter_data_service.get_filter_item(filter_id)
		if filter_data is None:
			return None
		slide_path = self.slide_path_provider.get_slide_path() if isinstance(self.slide_path_provider,
																			 SlidePathProvider) else self.slide_path_provider()
		if slide_path is None:
			return None

		cache_key = str(hashkey(self.filter_processor.filter_task_key(filter_data, slide_path, annotation_model)))
		# cache_key = self.filter_processor2.task_key(annotation_id)
		pixmap = QPixmapCache.find(cache_key)
		filter_results = cache_.get(cache_key)
		# print(str(cache_key), pixmap)
		if pixmap and filter_results:
			# TODO hack, edit_filter_results must be explicit and not in get_pixmap
			# print("filter_results")
			self.annotation_service.edit_filter_results(annotation_id, filter_results)
			return filter_level, pixmap
		else:
			# print("try lock", cache_key)
			with self.scheduled_or_running_tasks_lock:
				# print("lock received", cache_key)
				annotation_tasks = self.scheduled_or_running_tasks[annotation_id]
				if cache_key in annotation_tasks:
					actual_task = annotation_tasks[cache_key]
					if not actual_task.cancelled() and not is_task_outdated(actual_task):
						add_task_success_callback(actual_task, ready_callback)
					# actual_task.add_done_callback(not_canceled_done_callback(ready_callback))
					new_task = None
				else:
					for old_cache_key in annotation_tasks:
						old_task = annotation_tasks[old_cache_key]
						if old_task.cancel():
							# Successfully canceled scheduled(submitted) but not started task.
							pass
						else:
							# Failed to cancel task because it already has started. We cant kill it.
							# All we can do is to mark this task as "outdated" and then when task will finish we will ignore it results.
							mark_task_outdated(old_task)

					# filter_task = self.filter_processor.filter_task(filter_data, slide_path, annotation_model)
					# new_task = self.pool.submit(filter_task)
					# self.scheduled_or_running_tasks[annotation_id][cache_key] = new_task
					# print("new_task submitted", cache_key)
					# task_callback = build_task_callback(annotation_id, cache_key, ready_callback)
					# set_task_filter_future_signals(new_task, FilterFutureSignals())
					# get_task_filter_future_signals(new_task).result.connect(self.on_done_in_gui_thread)
					new_task = self.submit_task(annotation_id, cache_key, filter_data, slide_path, annotation_model)
			# print("lock released", cache_key)
			if new_task:
				task_callback = build_task_callback(annotation_id, cache_key)
				add_task_success_callback(new_task, ready_callback)
				new_task.add_done_callback(task_callback)
			return None

	def submit_task(self, annotation_id: str, cache_key, filter_data, slide_path, annotation_model) -> Future:
		filter_task = self.filter_processor.filter_task(filter_data, slide_path, annotation_model)
		new_task = self.pool.submit(filter_task)
		self.scheduled_or_running_tasks[annotation_id][cache_key] = new_task
		# print("new_task submitted", cache_key)
		set_task_filter_future_signals(new_task, FilterFutureSignals())
		get_task_filter_future_signals(new_task).result.connect(self.on_done_in_gui_thread)
		return new_task

	def on_done_in_gui_thread(self, annotation_id: str, cache_key: str, filter_output: FilterOutput, success_callbacks):
		# print("on_done_in_gui_thread try lock", cache_key)
		with self.scheduled_or_running_tasks_lock:
			# print("on_done_in_gui_thread lock received", cache_key)
			del self.scheduled_or_running_tasks[annotation_id][cache_key]
		# print("on_done_in_gui_thread lock released", cache_key)

		pixmap = QPixmap.fromImage(filter_output.img)
		if filter_output.bool_mask_ndimg is not None:
			bitmap = ndimg_to_bitmap(filter_output.bool_mask_ndimg)
			pixmap.setMask(bitmap)
		QPixmapCache.insert(cache_key, pixmap)
		cache_[cache_key] = filter_output.results
		self.annotation_service.edit_filter_results(annotation_id, filter_output.results)
		for callback in success_callbacks:
			callback()
