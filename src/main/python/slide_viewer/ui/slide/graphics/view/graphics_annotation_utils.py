from PyQt5.QtGui import QColor

from common_qt.qobjects_convert_util import ituples_to_qpoints, ituple_to_qpoint
from deepable.core import deep_get, deep_contains
from slide_viewer.ui.common.model import AnnotationModel
from slide_viewer.ui.slide.graphics.item.annotation.annotation_figure_graphics_item import AnnotationFigureGraphicsModel
from slide_viewer.ui.slide.graphics.item.annotation.annotation_graphics_item import AnnotationGraphicsModel
from slide_viewer.ui.slide.graphics.item.annotation.annotation_text_graphics_item import AnnotationTextGraphicsModel


def build_annotation_figure_graphics_model(m: AnnotationModel) -> AnnotationFigureGraphicsModel:
	return AnnotationFigureGraphicsModel(m.geometry.annotation_type,
										 ituples_to_qpoints(m.geometry.points),
										 QColor(m.figure_graphics_view_config.color))


def build_annotation_text_graphics_model(m: AnnotationModel) -> AnnotationTextGraphicsModel:
	display_patterns = m.text_graphics_view_config.display_pattern.split("\\n")
	text_display_values = [display_pattern.format_map(m.dict()) for display_pattern in display_patterns]
	if m.stats:
		text_display_values.extend([v for v in [m.stats.area_text, m.stats.length_text] if v])
	if m.filter_results:
		text_display_values.extend([v for k, v in m.filter_results.items() if v and str(k).endswith("_text")])
	# text = '\n'.join(map(str, text_display_values))
	text = '<br/>'.join(map(str, text_display_values))
	return AnnotationTextGraphicsModel(text, QColor(m.text_graphics_view_config.background_color))


def build_annotation_graphics_model(m: AnnotationModel) -> AnnotationGraphicsModel:
	text_model = build_annotation_text_graphics_model(m)
	figure_model = build_annotation_figure_graphics_model(m)
	return AnnotationGraphicsModel(ituple_to_qpoint(m.geometry.origin_point), figure_model, text_model,
								   m.figure_graphics_view_config.hidden, m.text_graphics_view_config.hidden)
