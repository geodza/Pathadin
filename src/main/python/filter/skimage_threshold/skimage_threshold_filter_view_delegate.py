import typing

from PyQt5.QtCore import QSize
from PyQt5.QtWidgets import QWidget, QStyleOptionViewItem, QMenu

from common_qt.action.my_menu import create_menu
from common_qt.editor.dropdown import Dropdown, commit_close_after_dropdown_select
from common_qt.mvc.model.delegate.item_model_delegate import AbstractItemModelDelegate
from common_qt.mvc.view.delegate.abstract_item_view_context_menu_delegate import AbstractItemViewContextMenuDelegate
from common_qt.mvc.view.delegate.abstract_item_view_delegate import AbstractItemViewDelegate
from deepable.core import first_last_keys, deep_keys
from deepable_qt.model.deepable_model_index import DeepableQModelIndex
from deepable_qt.model.deepable_tree_model import DeepableTreeModel
from deepable_qt.model.standard_deepable_tree_model_delegate import StandardDeepableTreeModelDelegate
from deepable_qt.view.deepable_tree_view import DeepableTreeView
from filter_template.filter_template_item_model_delegate_factory import FilterTemplateItemModelDelegateFactory, \
	FilterTemplateItemModelDelegate
from filter_template.filter_template_item_view_context_menu_delegate import FilterTemplateItemViewContextMenuDelegate
from filter_template.filter_template_item_view_context_menu_delegate_factory import \
	FilterTemplateItemViewContextMenuDelegateFactory
from filter_template.filter_template_item_view_delegate import ImmutableFilterTemplateTreeViewDelegate
from filter_template.filter_template_item_viewl_delegate_factory import FilterTemplateItemViewDelegateFactory
from filter.skimage_threshold.skimage_threshold_filter_model import SkimageMinimumThresholdParams, \
	SkimageThresholdFilterData_, \
	SkimageThresholdType, SkimageThresholdFilterData, SkimageMeanThresholdFilterData, \
	SkimageMinimumThresholdFilterData

I = DeepableQModelIndex
M = DeepableTreeModel
V = DeepableTreeView
F = SkimageThresholdFilterData


class SkimageThresholdFilterContextMenuDelegateFactory(FilterTemplateItemViewContextMenuDelegateFactory):

	def _create_delegate(self, index: I, view: V, filter_data) -> typing.Optional[
		AbstractItemViewContextMenuDelegate[I, V]]:
		if not index.isValid():
			return SkimageThresholdFilterContextMenuDelegate(view)
		elif isinstance(filter_data, (SkimageMinimumThresholdFilterData, SkimageMeanThresholdFilterData)):
			return SkimageThresholdFilterContextMenuDelegate(view)
		else:
			return None


class SkimageThresholdFilterContextMenuDelegate(FilterTemplateItemViewContextMenuDelegate):

	def create_menu(self, index: I) -> typing.Optional[QMenu]:
		# Index may be invalid => no model for invalid index. So take model from view.
		model = self.view.model()
		if not index.isValid():
			actions = [
				self.create_add_action("Add skimage minimum filter", "skimage_min_filter_",
									   lambda k: SkimageMinimumThresholdFilterData(k, k)),
				self.create_add_action("Add skimage mean filter", "skimage_mean_filter_",
									   lambda k: SkimageMeanThresholdFilterData(k, k))
			]
			menu = create_menu("Skimage threshold", actions)
			return menu
		else:
			return None


class SkimageThresholdFilterModelDelegateFactory(FilterTemplateItemModelDelegateFactory):

	def _create(self, index: I, filter_data: F) -> typing.Optional[AbstractItemModelDelegate[I]]:
		if isinstance(filter_data, F):
			# F here is not a single class but a hierarchy of classes.
			# There are about 12 threshold filters in skimage: https://scikit-image.org/docs/dev/api/skimage.filters.html
			# We will try to handle all of them in one plugin, not in 12 plugins.
			return SkimageThresholdFilterModelDelegate()


class SkimageThresholdFilterModelDelegate(FilterTemplateItemModelDelegate):

	def _is_index_readonly(self, index: I) -> bool:
		model = index.model()
		key, value = model.key(index), model.value(index)
		filter_key, last_key = first_last_keys(key)
		filter_data = model[filter_key]
		if index.column() == 1:
			if last_key == SkimageThresholdFilterData_.skimage_threshold_type:
				return False
			elif isinstance(filter_data, SkimageMeanThresholdFilterData):
				return super()._is_index_readonly(index)
			elif isinstance(filter_data, SkimageMinimumThresholdFilterData):
				keys = deep_keys(SkimageMinimumThresholdParams)
				if last_key in keys:
					return False

		return super()._is_index_readonly(index)


class SkimageThresholdFilterViewDelegateFactory(FilterTemplateItemViewDelegateFactory):

	def _create(self, index: I, filter_data) -> typing.Optional[AbstractItemViewDelegate[I, M, V]]:
		if isinstance(filter_data, F):
			return SkimageThresholdFilterViewDelegate()


class SkimageThresholdFilterViewDelegate(ImmutableFilterTemplateTreeViewDelegate):

	def filter_data_type(self, filter_data_dict: dict) -> type:
		print(filter_data_dict)
		print(SkimageThresholdFilterData_.skimage_threshold_type)
		print(filter_data_dict[SkimageThresholdFilterData_.skimage_threshold_type])
		skimage_threshold_type = SkimageThresholdType[
			filter_data_dict[SkimageThresholdFilterData_.skimage_threshold_type]]
		if skimage_threshold_type == SkimageThresholdType.threshold_mean:
			return SkimageMeanThresholdFilterData
		elif skimage_threshold_type == SkimageThresholdType.threshold_minimum:
			return SkimageMinimumThresholdFilterData
		else:
			raise ValueError()

	def _createEditor(self, parent: QWidget, option: QStyleOptionViewItem, index: I, key: str,
					  filter_data: F) -> QWidget:
		model = index.model()
		filter_key, last_key = first_last_keys(key)
		filter_data = model[filter_key]
		value = model.value(index)
		if last_key == SkimageThresholdFilterData_.skimage_threshold_type:
			dropdown = Dropdown(list(SkimageThresholdType), value, parent)
			return commit_close_after_dropdown_select(self._itd, dropdown)
		elif isinstance(filter_data, SkimageMeanThresholdFilterData):
			return super()._createEditor(parent, option, index, key, filter_data)
		elif isinstance(filter_data, SkimageMinimumThresholdFilterData):
			keys = deep_keys(SkimageMinimumThresholdParams)
			if last_key in keys:
				return super()._createEditor(parent, option, index, key, filter_data)
		super()._createEditor(parent, option, index, key, filter_data)

	def _sizeHint(self, option: QStyleOptionViewItem, index: I, key: str) -> QSize:
		return super()._sizeHint(option, index, key)
