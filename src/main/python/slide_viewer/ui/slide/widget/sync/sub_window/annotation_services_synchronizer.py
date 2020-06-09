from typing import List, Callable

from dataclasses import dataclass

from slide_viewer.ui.slide.widget.annotation.annotation_service import AnnotationService


@dataclass(frozen=True)
class AnnotationServiceSyncOptions:
	annotations: bool = False
	annotations_filters: bool = False


def sync_annotation_services(service: AnnotationService,
							 sub_services_except_active: List[AnnotationService],
							 options: AnnotationServiceSyncOptions) \
		-> Callable[[], None]:
	def cleanup():
		for sub_service in sub_services_except_active:
			if options.annotations:
				service.added_signal().disconnect(sub_service.add_copy_or_edit_with_copy);
				service.deleted_signal().disconnect(sub_service.delete_if_exist)

				if options.annotations_filters:
					service.edited_signal().disconnect(sub_service.add_or_edit_with_copy)
				else:
					service.edited_signal().disconnect(sub_service.add_or_edit_with_copy_without_filter)

	for sub_service in sub_services_except_active:
		if options.annotations:
			service.added_signal().connect(sub_service.add_copy_or_edit_with_copy)
			service.deleted_signal().connect(sub_service.delete_if_exist)

			if options.annotations_filters:
				service.edited_signal().connect(sub_service.add_or_edit_with_copy)
			else:
				service.edited_signal().connect(sub_service.add_or_edit_with_copy_without_filter)
	return cleanup


class AnnotationServicesSynchronizer:
	def __init__(self):
		self._cleanup = None

	def sync(self, _source: AnnotationService,
			 _targets: List[AnnotationService],
			 _options: AnnotationServiceSyncOptions,
			 ):
		if self._cleanup:
			self._cleanup()
			self._cleanup = None
		if _source:
			service = _source
			sub_services_except_active = [sw for sw in _targets if sw is not service]
			# print(f"active view: {view}")
			cleanup = sync_annotation_services(service, sub_services_except_active, _options)
			self._cleanup = cleanup
