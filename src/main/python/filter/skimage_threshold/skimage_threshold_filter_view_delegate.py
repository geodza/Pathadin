import typing

from PyQt5.QtCore import QModelIndex, Qt, QSize
from PyQt5.QtWidgets import QWidget, QStyleOptionViewItem

from common_qt.editor.dropdown import Dropdown, commit_close_after_dropdown_select
from common_qt.mvc.model.delegate.item_model_delegate import AbstractItemModelDelegate
from common_qt.mvc.view.delegate.item_view_delegate import AbstractItemViewDelegate
from deepable.core import deep_set, first_last_keys, deep_keys
from deepable_qt.model.deepable_model_index import DeepableQModelIndex
from deepable_qt.model.deepable_tree_model import DeepableTreeModel
from deepable_qt.model.standard_deepable_tree_model_delegate import StandardDeepableTreeModelDelegate
from deepable_qt.view.deepable_tree_view import DeepableTreeView
from filter_template.filter_template_item_model_delegate_factory import FilterTemplateItemModelDelegateFactory
from filter_template.filter_template_item_view_delegate import ImmutableFilterTemplateTreeViewDelegate
from filter_template.filter_template_item_viewl_delegate_factory import FilterTemplateItemViewDelegateFactory
from img.filter.skimage_threshold import SkimageMinimumThresholdParams, SkimageAutoThresholdFilterData_, \
	SkimageThresholdType, SkimageAutoThresholdFilterData, SkimageMeanThresholdFilterData, \
	SkimageMinimumThresholdFilterData

T = DeepableQModelIndex
M = DeepableTreeModel
V = DeepableTreeView
F = SkimageAutoThresholdFilterData


class SkimageThresholdFilterModelDelegateFactory(FilterTemplateItemModelDelegateFactory):

	def _create(self, index: T, filter_data: F) -> typing.Optional[AbstractItemModelDelegate[T]]:
		if isinstance(filter_data, F):
			# F here is not a single class but a hierarchy of classes.
			# There are about 12 threshold filters in skimage: https://scikit-image.org/docs/dev/api/skimage.filters.html
			# We will try to handle all of them in one plugin, not in 12 plugins.
			return SkimageThresholdFilterModelDelegate()


class SkimageThresholdFilterModelDelegate(StandardDeepableTreeModelDelegate):

	def _is_index_readonly(self, index: T) -> bool:
		model = index.model()
		key, value = model.key(index), model.value(index)
		filter_key, last_key = first_last_keys(key)
		filter_data = model[filter_key]
		if index.column() == 1:
			if last_key == SkimageAutoThresholdFilterData_.skimage_threshold_type:
				return False
			elif isinstance(filter_data, SkimageMeanThresholdFilterData):
				return super()._is_index_readonly(index)
			elif isinstance(filter_data, SkimageMinimumThresholdFilterData):
				keys = deep_keys(SkimageMinimumThresholdParams)
				if last_key in keys:
					return False

		return super()._is_index_readonly(index)


class SkimageThresholdFilterViewDelegateFactory(FilterTemplateItemViewDelegateFactory):

	def _create(self, index: T, filter_data) -> typing.Optional[AbstractItemViewDelegate[T, M, V]]:
		if isinstance(filter_data, F):
			return SkimageThresholdFilterViewDelegate()


class SkimageThresholdFilterViewDelegate(ImmutableFilterTemplateTreeViewDelegate):

	def filter_data_type(self, filter_data_dict: dict) -> type:
		print(filter_data_dict)
		print(SkimageAutoThresholdFilterData_.skimage_threshold_type)
		print(filter_data_dict[SkimageAutoThresholdFilterData_.skimage_threshold_type])
		skimage_threshold_type = SkimageThresholdType[
			filter_data_dict[SkimageAutoThresholdFilterData_.skimage_threshold_type]]
		if skimage_threshold_type == SkimageThresholdType.threshold_mean:
			return SkimageMeanThresholdFilterData
		elif skimage_threshold_type == SkimageThresholdType.threshold_minimum:
			return SkimageMinimumThresholdFilterData
		else:
			raise ValueError()

	def _createEditor(self, parent: QWidget, option: QStyleOptionViewItem, index: T, key: str,
					  filter_data: F) -> QWidget:
		model = index.model()
		filter_key, last_key = first_last_keys(key)
		filter_data = model[filter_key]
		value = model.value(index)
		if last_key == SkimageAutoThresholdFilterData_.skimage_threshold_type:
			dropdown = Dropdown(list(SkimageThresholdType), value, parent)
			return commit_close_after_dropdown_select(self._itd, dropdown)
		elif isinstance(filter_data, SkimageMeanThresholdFilterData):
			return super()._createEditor(parent, option, index, key, filter_data)
		elif isinstance(filter_data, SkimageMinimumThresholdFilterData):
			keys = deep_keys(SkimageMinimumThresholdParams)
			if last_key in keys:
				return super()._createEditor(parent, option, index, key, filter_data)
		super()._createEditor(parent, option, index, key, filter_data)

	def _sizeHint(self, option: QStyleOptionViewItem, index: T, key: str) -> QSize:
		return super()._sizeHint(option, index, key)
