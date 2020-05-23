import typing
from typing import cast

from PyQt5 import QtCore
from PyQt5.QtCore import QModelIndex, Qt, QSize
from PyQt5.QtWidgets import QWidget, QStyleOptionViewItem
from dataclasses import replace

from common_qt.editor.range.gray_range_editor import GrayRangeEditor
from common_qt.editor.range.hsv_range_editor import HSVRangeEditor
from common_qt.mvc.model.delegate.item_model_delegate import AbstractItemModelDelegate
from common_qt.mvc.view.delegate.item_view_delegate import AbstractItemViewDelegate
from deepable.core import deep_set, first_last_keys
from deepable_qt.model.deepable_model_index import DeepableQModelIndex
from deepable_qt.model.deepable_tree_model import DeepableTreeModel
from deepable_qt.model.standard_deepable_tree_model_delegate import StandardDeepableTreeModelDelegate
from deepable_qt.view.deepable_tree_view import DeepableTreeView
from filter_template.filter_template_item_model_delegate_factory import FilterTemplateItemModelDelegateFactory
from filter_template.filter_template_item_view_delegate import ImmutableFilterTemplateTreeViewDelegate
from filter_template.filter_template_item_viewl_delegate_factory import FilterTemplateItemViewDelegateFactory
from img.filter.base_filter import FilterData
from img.filter.manual_threshold import HSVManualThresholdFilterData, HSVManualThresholdFilterData_

T = DeepableQModelIndex
M = DeepableTreeModel
V = DeepableTreeView


class HSVManualThresholdFilterModelDelegateFactory(FilterTemplateItemModelDelegateFactory):

	def _create(self, index: T, filter_data) -> typing.Optional[AbstractItemModelDelegate[T]]:
		if isinstance(filter_data, HSVManualThresholdFilterData):
			return HSVManualThresholdFilterModelDelegate()


class HSVManualThresholdFilterModelDelegate(StandardDeepableTreeModelDelegate):

	def _is_index_readonly(self, index: T) -> bool:
		model = index.model()
		key, value = model.key(index), model.value(index)
		filter_key, last_key = first_last_keys(key)
		filter_data: FilterData = model[filter_key]
		# print(f"_is_index_readonly {last_key}")
		if index.column() == 1 and last_key == HSVManualThresholdFilterData_.hsv_range:
			return False
		return super()._is_index_readonly(index)


class HSVManualThresholdFilterViewDelegateFactory(FilterTemplateItemViewDelegateFactory):

	def _create(self, index: T, filter_data) -> typing.Optional[AbstractItemViewDelegate[T, M, V]]:
		if isinstance(filter_data, HSVManualThresholdFilterData):
			return HSVManualThresholdFilterTreeViewDelegate()


class HSVManualThresholdFilterTreeViewDelegate(ImmutableFilterTemplateTreeViewDelegate):

	def filter_data_type(self, filter_data_dict: dict) -> type:
		return HSVManualThresholdFilterData

	def _createEditor(self, parent: QWidget, option: QStyleOptionViewItem, index: T, key: str,
					  filter_data: HSVManualThresholdFilterData) -> QWidget:
		model = index.model()
		filter_key, last_key = first_last_keys(key)
		print(f"_createEditor {last_key}")
		if last_key == HSVManualThresholdFilterData_.hsv_range:
			def on_threshold_range_change(range_):
				new_filter_data = replace(filter_data,
										  **{HSVManualThresholdFilterData_.hsv_range: range_})
				model[filter_key] = new_filter_data

			editor = HSVRangeEditor(parent)
			if filter_data.realtime:
				editor.hsvRangeChanged.connect(on_threshold_range_change)
			return editor
		return super()._createEditor(parent, option, index, key, filter_data)

	def _sizeHint(self, option: QStyleOptionViewItem, index: T, key: str) -> QSize:
		*leading_keys, last_key = key.split('.')
		if last_key == HSVManualThresholdFilterData_.hsv_range:
			return QSize(100, 300)
		return super()._sizeHint(option, index, key)
