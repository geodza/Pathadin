from typing import Callable, List

from annotation.model import AnnotationModel
from common.log_utils import log
from common_qt.util.debounce import qt_debounce
from common_qt.util.slot_disconnected_utils import slot_disconnected
from slide_viewer.ui.slide.widget.annotation.annotation_service import AnnotationService
from slide_viewer.ui.slide.widget.annotation.annotation_stats_processor import AnnotationStatsProcessor


def sync_annotations_stats(annotation_service: AnnotationService, microns_per_pixel_provider: Callable[[], float]):
	annotation_stats_processor = AnnotationStatsProcessor(microns_per_pixel_provider=microns_per_pixel_provider)

	@qt_debounce(0.2)
	def on_annotation_model_edited(id_: str, model: AnnotationModel):
		with slot_disconnected(annotation_service.edited_signal(), on_annotation_model_edited):
			stats = annotation_stats_processor.calc_stats(model)
			# Need to check if annotation is present because it can be deleted during qt_debounce time.
			if annotation_service.has(id_):
				annotation_service.edit_stats(id_, stats)

	annotation_service.edited_signal().connect(on_annotation_model_edited)

