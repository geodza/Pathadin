import typing
from typing import cast

from PyQt5 import QtCore
from PyQt5.QtCore import QModelIndex, Qt, QSize
from PyQt5.QtWidgets import QWidget, QStyleOptionViewItem
from dataclasses import replace

from common_qt.editor.dropdown import Dropdown, commit_close_after_dropdown_select
from common_qt.editor.file_path_editor import FilePathEditor
from common_qt.editor.range.gray_range_editor import GrayRangeEditor
from common_qt.editor.range.hsv_range_editor import HSVRangeEditor
from common_qt.mvc.model.delegate.factory.item_model_delegate_factory import AbstractItemModelDelegateFactory
from common_qt.mvc.model.delegate.item_model_delegate import AbstractItemModelDelegate
from common_qt.mvc.view.delegate.factory.item_view_delegate_factory import AbstractItemViewDelegateFactory
from common_qt.mvc.view.delegate.item_view_delegate import AbstractItemViewDelegate
from deepable.convert import deep_to_dict, deep_from_dict
from deepable.core import deep_set, first_last_keys, deep_keys
from deepable_qt.model.deepable_model_index import DeepableQModelIndex
from deepable_qt.model.deepable_tree_model import DeepableTreeModel
from deepable_qt.model.standard_deepable_tree_model_delegate import StandardDeepableTreeModelDelegate
from deepable_qt.view.deepable_tree_view import DeepableTreeView
from filter_template.filter_template_item_model_delegate_factory import FilterTemplateItemModelDelegateFactory
from filter_template.filter_template_item_view_delegate import ImmutableFilterTemplateTreeViewDelegate
from filter_template.filter_template_item_viewl_delegate_factory import FilterTemplateItemViewDelegateFactory
from img.filter.base_filter import FilterData

from img.filter.keras_model import KerasModelParams, KerasModelFilterData, KerasModelParams_
from img.filter.manual_threshold import HSVManualThresholdFilterData, HSVManualThresholdFilterData_

T = DeepableQModelIndex
M = DeepableTreeModel
V = DeepableTreeView
F = KerasModelFilterData


class KerasModelFilterModelDelegateFactory(FilterTemplateItemModelDelegateFactory):

	def _create(self, index: T, filter_data: F) -> typing.Optional[AbstractItemModelDelegate[T]]:
		if isinstance(filter_data, KerasModelFilterData):
			return KerasModelFilterModelDelegate()


class KerasModelFilterModelDelegate(StandardDeepableTreeModelDelegate):

	def _is_index_readonly(self, index: T) -> bool:
		model = index.model()
		key, value = model.key(index), model.value(index)
		filter_key, last_key = first_last_keys(key)
		filter_data: FilterData = model[filter_key]
		# print(f"_is_index_readonly {last_key}")
		keys = deep_keys(KerasModelParams)
		if index.column() == 1 and last_key in keys:
			return False
		return super()._is_index_readonly(index)


class KerasModelFilterViewDelegateFactory(FilterTemplateItemViewDelegateFactory):

	def _create(self, index: T, filter_data: F) -> typing.Optional[AbstractItemViewDelegate[T, M, V]]:
		if isinstance(filter_data, KerasModelFilterData):
			return KerasModelFilterViewDelegate()


class KerasModelFilterViewDelegate(ImmutableFilterTemplateTreeViewDelegate):

	def filter_data_type(self, filter_data_dict: dict) -> type:
		return KerasModelFilterData

	def _createEditor(self, parent: QWidget, option: QStyleOptionViewItem, index: T, key: str,
					  filter_data: F) -> QWidget:
		model = index.model()
		filter_key, last_key = first_last_keys(key)
		value = model.value(index)
		# keys = deep_keys(KerasModelParams)
		if last_key == KerasModelParams_.model_path:
			file_path_editor = FilePathEditor(parent, value)
			return file_path_editor

		return super()._createEditor(parent, option, index, key, filter_data)

	def _sizeHint(self, option: QStyleOptionViewItem, index: T, key: str) -> QSize:
		return super()._sizeHint(option, index, key)
