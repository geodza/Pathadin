from typing import Optional, cast

from PyQt5 import QtCore
from PyQt5.QtCore import QModelIndex, QObject, QSize, pyqtBoundSignal
from PyQt5.QtWidgets import QWidget, QStyledItemDelegate, \
	QStyleOptionViewItem
from dataclasses import dataclass, InitVar, replace

from common_image.model.color_mode import ColorMode
from deepable.convert import deep_to_dict, deep_from_dict
from deepable_qt.deepable_tree_model import DeepableTreeModel
from img.filter.base_filter import FilterData, FilterData_, FilterType
from img.filter.keras_model import KerasModelFilterData, KerasModelParams, KerasModelParams_
from img.filter.kmeans_filter import KMeansFilterData, KMeansInitType, KMeansParams_
from img.filter.manual_threshold import ManualThresholdFilterData, ManualThresholdFilterData_, \
	GrayManualThresholdFilterData, GrayManualThresholdFilterData_, HSVManualThresholdFilterData, \
	HSVManualThresholdFilterData_, color_mode_to_filter_type
from img.filter.nuclei import NucleiFilterData, NucleiParams
from img.filter.positive_pixel_count import PositivePixelCountFilterData, PositivePixelCountParams
from img.filter.skimage_threshold import SkimageThresholdType, SkimageAutoThresholdFilterData, \
	SkimageAutoThresholdFilterData_, SkimageMeanThresholdFilterData, SkimageMinimumThresholdFilterData, \
	SkimageMinimumThresholdParams_
from img.filter.threshold_filter import ThresholdFilterData, ThresholdFilterData_, \
	ThresholdType
from common_qt.editor.dropdown import Dropdown
from common_qt.editor.file_path_editor import FilePathEditor
from common_qt.editor.list_editor import SelectListEditor
from common_qt.editor.range.gray_range_editor import GrayRangeEditor
from common_qt.editor.range.hsv_range_editor import HSVRangeEditor
from deepable.core import toplevel_key, deep_set, deep_keys, deep_get


def commit_close_after_dropdown_select(delegate: QStyledItemDelegate, dropdown: Dropdown) -> Dropdown:
	def on_selected_item_changed(item):
		delegate.commitData.emit(dropdown)
		delegate.closeEditor.emit(dropdown)

	dropdown.selectedItemChanged.connect(on_selected_item_changed)
	cast(pyqtBoundSignal, dropdown.activated).connect(on_selected_item_changed)
	return dropdown


@dataclass
# delegate is coupled to concrete model
class FilterTreeViewDelegate(QStyledItemDelegate):
	model: DeepableTreeModel
	parent_: InitVar[Optional[QObject]] = None

	# filterDataChanged = pyqtSignal(FilterData)

	def __post_init__(self, parent_: Optional[QObject]):
		QStyledItemDelegate.__init__(self, parent_)

	def createEditor(self, parent: QWidget, option: QStyleOptionViewItem, index: QModelIndex) -> QWidget:
		key, value = self.model.key(index), self.model.value(index)
		filter_id = toplevel_key(key)
		filter_data: FilterData = self.model[filter_id]
		key = key.split('.')[-1]
		if key == FilterData_.filter_type:
			dropdown = Dropdown(list(FilterType), value, parent)
			return commit_close_after_dropdown_select(self, dropdown)
		elif key == FilterData_.realtime:
			return super().createEditor(parent, option, index)
		elif isinstance(filter_data, ThresholdFilterData):
			if key == ThresholdFilterData_.threshold_type:
				dropdown = Dropdown(list(ThresholdType), value, parent)
				return commit_close_after_dropdown_select(self, dropdown)
			elif isinstance(filter_data, ManualThresholdFilterData):
				if key == ManualThresholdFilterData_.color_mode:
					color_modes = set(ColorMode)  # - {ColorMode.RGB}
					dropdown = Dropdown(list(color_modes), value, parent)
					return commit_close_after_dropdown_select(self, dropdown)
				elif isinstance(filter_data, HSVManualThresholdFilterData):
					# self.sizeHintChanged.emit(index.sibling(index.row() + 1, index.column()))
					if key == HSVManualThresholdFilterData_.hsv_range:
						def on_threshold_range_change(range_):
							new_filter_data = replace(filter_data,
													  **{HSVManualThresholdFilterData_.hsv_range: range_})
							self.model[filter_id] = new_filter_data

						# self.filterDataChanged.emit(new_filter_data)

						editor = HSVRangeEditor(parent)
						if filter_data.realtime:
							editor.hsvRangeChanged.connect(on_threshold_range_change)
						return editor
					else:
						raise ValueError(f"Unknown key {key} for filter {filter_data}")
				elif isinstance(filter_data, GrayManualThresholdFilterData):
					# self.sizeHintChanged.emit(index.sibling(index.row() + 1, index.column()))
					if key == GrayManualThresholdFilterData_.gray_range:
						def on_threshold_range_change(range_):
							self.model[filter_id] = replace(filter_data,
															**{GrayManualThresholdFilterData_.gray_range: range_})

						editor = GrayRangeEditor(parent)
						if filter_data.realtime:
							editor.grayRangeChanged.connect(on_threshold_range_change)
						return editor
					else:
						return  super().createEditor(parent, option, index)
						# raise ValueError(f"Unknown key {key} for filter {filter_data}")
				else:
					raise ValueError(f"Unknown key {key} for filter {filter_data}")
			elif isinstance(filter_data, SkimageAutoThresholdFilterData):
				if key == SkimageAutoThresholdFilterData_.skimage_threshold_type:
					dropdown = Dropdown(list(SkimageThresholdType), value, parent)
					return commit_close_after_dropdown_select(self, dropdown)
				else:
					if isinstance(filter_data, SkimageMeanThresholdFilterData):
						raise ValueError(f"Unknown key {key} for filter {filter_data}")
					elif isinstance(filter_data, SkimageMinimumThresholdFilterData):
						if key in (SkimageMinimumThresholdParams_.max_iter, SkimageMinimumThresholdParams_.nbins):
							return super().createEditor(parent, option, index)
						else:
							raise ValueError(f"Unknown key {key} for filter {filter_data}")
					else:
						raise ValueError(f"Unknown key {key} for filter {filter_data}")
		elif isinstance(filter_data, KMeansFilterData):
			if key == KMeansParams_.init:
				dropdown = Dropdown(list(KMeansInitType), value, parent)
				return commit_close_after_dropdown_select(self, dropdown)
			elif key in (KMeansParams_.max_iter, KMeansParams_.n_clusters,
						 KMeansParams_.n_init, KMeansParams_.precompute_distances,
						 KMeansParams_.random_state, KMeansParams_.tol):
				return super().createEditor(parent, option, index)
			else:
				raise ValueError(f"Unknown key {key} for filter {filter_data}")
		elif isinstance(filter_data, NucleiFilterData):
			keys = deep_keys(NucleiParams)
			if key in keys:
				return super().createEditor(parent, option, index)
			else:
				raise ValueError(f"Unknown key {key} for filter {filter_data}")
		elif isinstance(filter_data, PositivePixelCountFilterData):
			keys = deep_keys(PositivePixelCountParams)
			if key in keys:
				return super().createEditor(parent, option, index)
			else:
				raise ValueError(f"Unknown key {key} for filter {filter_data}")
		elif isinstance(filter_data, KerasModelFilterData):
			keys = deep_keys(KerasModelParams)
			if key == KerasModelParams_.model_path:
				file_path_editor = FilePathEditor(parent, value)
				return file_path_editor
			elif key in keys:
				return super().createEditor(parent, option, index)
			else:
				raise ValueError(f"Unknown key {key} for filter {filter_data}")
		else:
			raise ValueError(f"Unknown filter type {filter_data}")

		return super().createEditor(parent, option, index)

	# def setEditorData(self, editor: QWidget, index: QtCore.QModelIndex) -> None:
	#     super().setEditorData(editor, index)

	def setModelData(self, editor: QWidget, model: QtCore.QAbstractItemModel, index: QtCore.QModelIndex) -> None:
		key, value = self.model.key(index), self.model.value(index)
		filter_id, *attr_path = key.split('.')
		filter_data: FilterData = self.model[filter_id]
		value = editor.metaObject().userProperty().read(editor)
		# print(f"{key} {value}")
		filter_data_dict = deep_to_dict(filter_data)
		deep_set(filter_data_dict, '.'.join(attr_path), value)

		filter_type = FilterType(filter_data_dict.get(FilterData_.filter_type, FilterType.THRESHOLD))
		if filter_type == FilterType.THRESHOLD:
			threshold_type = ThresholdType(
				filter_data_dict.get(ThresholdFilterData_.threshold_type, ThresholdType.MANUAL))
			if threshold_type == ThresholdType.MANUAL:
				color_mode = ColorMode(filter_data_dict.get(ManualThresholdFilterData_.color_mode, ColorMode.L))
				if color_mode == ColorMode.HSV:
					target_type = HSVManualThresholdFilterData
				elif color_mode == ColorMode.L:
					target_type = GrayManualThresholdFilterData
				else:
					target_type = GrayManualThresholdFilterData
			elif threshold_type == ThresholdType.SKIMAGE_AUTO:
				skimage_threshold_type = SkimageThresholdType(
					filter_data_dict.get(SkimageAutoThresholdFilterData_.skimage_threshold_type,
										 SkimageThresholdType.threshold_mean))
				if skimage_threshold_type == SkimageThresholdType.threshold_mean:
					target_type = SkimageMeanThresholdFilterData
				elif skimage_threshold_type == SkimageThresholdType.threshold_minimum:
					target_type = SkimageMinimumThresholdFilterData
				else:
					target_type = SkimageMeanThresholdFilterData
			else:
				target_type = GrayManualThresholdFilterData
		elif filter_type == FilterType.KMEANS:
			target_type = KMeansFilterData
		elif filter_type == FilterType.NUCLEI:
			target_type = NucleiFilterData
		elif filter_type == FilterType.POSITIVE_PIXEL_COUNT:
			target_type = PositivePixelCountFilterData
		elif filter_type == FilterType.KERAS_MODEL:
			target_type = KerasModelFilterData
		else:
			target_type = GrayManualThresholdFilterData

		new_filter_data = deep_from_dict(filter_data_dict, target_type)
		print(new_filter_data)
		self.model[filter_id] = new_filter_data

	def updateEditorGeometry(self, editor: QWidget, option: QStyleOptionViewItem, index: QtCore.QModelIndex) -> None:
		if isinstance(editor, (SelectListEditor,)):
			# editor.setMinimumHeight(400)
			super().updateEditorGeometry(editor, option, index)
			# editor.setGeometry(option.rect)
			# editor.layout().setSizePolicy(QSizePolicy.MinimumExpanding, QSizePolicy.MinimumExpanding)
			# editor.set(QSizePolicy.MinimumExpanding, QSizePolicy.MinimumExpanding)
			if isinstance(editor, SelectListEditor):
				editor.adjustSize()
		# editor.update()
		elif isinstance(editor, Dropdown):
			super().updateEditorGeometry(editor, option, index)
			editor.showPopup()
		elif isinstance(editor, HSVRangeEditor):
			# editor.adjustSize()
			# editor.setMinimumHeight(400)
			# editor.update()
			super().updateEditorGeometry(editor, option, index)
		# editor.setGeometry(option.rect)
		# print(editor.size())
		elif isinstance(editor, FilePathEditor):
			# super().updateEditorGeometry(editor, option, index)
			editor.show_dialog()
		else:
			super().updateEditorGeometry(editor, option, index)

	def editorEvent(self, event: QtCore.QEvent, model: QtCore.QAbstractItemModel, option: QStyleOptionViewItem,
					index: QtCore.QModelIndex) -> bool:
		# print(event, index, option.type, option.widget, option.state)
		# print(option.state & QStyle.State_Editing == QStyle.State_Editing)
		# print(option.state, int(option.state), hex(option.state))
		return super().editorEvent(event, model, option, index)

	def sizeHint(self, option: QStyleOptionViewItem, index: QtCore.QModelIndex) -> QtCore.QSize:
		key, value = self.model.key(index), self.model.value(index)
		*leading_keys, last_key = key.split('.')
		filter_id = toplevel_key(key)
		filter_data: FilterData = self.model[filter_id]
		if isinstance(filter_data, ManualThresholdFilterData):
			if last_key in (HSVManualThresholdFilterData_.hsv_range, GrayManualThresholdFilterData_.gray_range):
				color_mode_to_size = {
					ColorMode.HSV: QSize(100, 400),
					ColorMode.L: QSize(0, 100),
				}
				return color_mode_to_size[filter_data.color_mode]
		return super().sizeHint(option, index)