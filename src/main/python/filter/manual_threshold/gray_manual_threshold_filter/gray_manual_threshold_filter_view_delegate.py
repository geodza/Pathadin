import typing

from PyQt5.QtCore import QSize
from PyQt5.QtWidgets import QWidget, QStyleOptionViewItem, QMenu
from dataclasses import replace

from common_qt.action.my_menu import create_menu
from common_qt.editor.range.gray_range_editor import GrayRangeEditor
from common_qt.mvc.view.delegate.abstract_item_view_context_menu_delegate import AbstractItemViewContextMenuDelegate
from common_qt.mvc.view.delegate.abstract_item_view_delegate import AbstractItemViewDelegate
from deepable.core import first_last_keys
from deepable_qt.model.deepable_model_index import DeepableQModelIndex
from deepable_qt.model.deepable_tree_model import DeepableTreeModel
from deepable_qt.view.deepable_tree_view import DeepableTreeView
from filter.common.filter_model import FilterData
from filter.manual_threshold.manual_threshold_filter_model import GrayManualThresholdFilterData, \
	GrayManualThresholdFilterData_
from filter_template.filter_template_item_model_delegate_factory import FilterTemplateItemModelDelegate
from filter_template.filter_template_item_view_context_menu_delegate import FilterTemplateItemViewContextMenuDelegate
from filter_template.filter_template_item_view_context_menu_delegate_factory import \
	FilterTemplateItemViewContextMenuDelegateFactory
from filter_template.filter_template_item_view_delegate import ImmutableFilterTemplateTreeViewDelegate
from filter_template.filter_template_item_viewl_delegate_factory import FilterTemplateItemViewDelegateFactory

I = DeepableQModelIndex
M = DeepableTreeModel
V = DeepableTreeView


class GrayManualThresholdFilterContextMenuDelegateFactory(FilterTemplateItemViewContextMenuDelegateFactory):

	def _create_delegate(self, index: I, view: V, filter_data) -> typing.Optional[
		AbstractItemViewContextMenuDelegate[I, V]]:
		if not index.isValid():
			return GrayManualThresholdFilterContextMenuDelegate(view)
		elif isinstance(filter_data, GrayManualThresholdFilterData):
			return GrayManualThresholdFilterContextMenuDelegate(view)
		else:
			return None


class GrayManualThresholdFilterContextMenuDelegate(FilterTemplateItemViewContextMenuDelegate):

	def create_menu(self, index: I) -> typing.Optional[QMenu]:
		actions = []
		# Index may be invalid => no model for invalid index. So take model from view.
		model = self.view.model()
		if not index.isValid():
			add_action = self.create_add_action("Add gray threshold filter", "gray_manual_threshold_filter_",
												lambda k: GrayManualThresholdFilterData(k, k))
			actions.append(add_action)
			menu = create_menu("Gray threshold", actions)
			return menu
		else:
			return None


class GrayManualThresholdFilterModelDelegate(FilterTemplateItemModelDelegate):

	def _is_index_readonly(self, index: I) -> bool:
		model = index.model()
		key, value = model.key(index), model.value(index)
		filter_key, last_key = first_last_keys(key)
		filter_data: FilterData = model[filter_key]
		if index.column() == 1:
			if last_key in (GrayManualThresholdFilterData_.gray_range):
				return False
			elif last_key in (GrayManualThresholdFilterData_.color_mode):
				return True
		return super()._is_index_readonly(index)


class GrayManualThresholdFilterViewDelegateFactory(FilterTemplateItemViewDelegateFactory):

	def _create(self, index: I, filter_data) -> typing.Optional[AbstractItemViewDelegate[I, M, V]]:
		if isinstance(filter_data, GrayManualThresholdFilterData):
			return GrayManualThresholdFilterViewDelegate()


class GrayManualThresholdFilterViewDelegate(ImmutableFilterTemplateTreeViewDelegate):

	def filter_data_type(self, filter_data_dict: dict) -> type:
		return GrayManualThresholdFilterData

	def _createEditor(self, parent: QWidget, option: QStyleOptionViewItem, index: I, key: str, filter_data) -> QWidget:
		model = index.model()
		filter_key, last_key = first_last_keys(key)
		filter_data: FilterData = model[filter_key]
		if last_key == GrayManualThresholdFilterData_.gray_range:
			def on_threshold_range_change(range_):
				model[filter_key] = replace(filter_data,
											**{GrayManualThresholdFilterData_.gray_range: range_})

			editor = GrayRangeEditor(parent)
			if filter_data.realtime:
				editor.grayRangeChanged.connect(on_threshold_range_change)
			return editor
		else:
			return super()._createEditor(parent, option, index, key, filter_data)

	def _sizeHint(self, option: QStyleOptionViewItem, index: I, key: str) -> QSize:
		*leading_keys, last_key = key.split('.')
		if last_key == GrayManualThresholdFilterData_.gray_range:
			return QSize(100, 300)
		return super()._sizeHint(option, index, key)
