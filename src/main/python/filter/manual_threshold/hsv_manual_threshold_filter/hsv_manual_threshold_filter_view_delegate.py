import typing

from PyQt5.QtCore import QSize
from PyQt5.QtWidgets import QWidget, QStyleOptionViewItem, QMenu
from dataclasses import replace

from common_qt.action.my_menu import create_menu
from common_qt.editor.range.hsv_range_editor import HSVRangeEditor
from common_qt.mvc.model.delegate.item_model_delegate import AbstractItemModelDelegate
from common_qt.mvc.view.delegate.abstract_item_view_context_menu_delegate import AbstractItemViewContextMenuDelegate
from common_qt.mvc.view.delegate.abstract_item_view_delegate import AbstractItemViewDelegate
from deepable.core import first_last_keys
from deepable_qt.model.deepable_model_index import DeepableQModelIndex
from deepable_qt.model.deepable_tree_model import DeepableTreeModel
from deepable_qt.view.deepable_tree_view import DeepableTreeView
from filter.common.filter_model import FilterData
from filter.manual_threshold.manual_threshold_filter_model import HSVManualThresholdFilterData, \
	HSVManualThresholdFilterData_
from filter_template.filter_template_item_model_delegate_factory import FilterTemplateItemModelDelegateFactory, \
	FilterTemplateItemModelDelegate
from filter_template.filter_template_item_view_context_menu_delegate import FilterTemplateItemViewContextMenuDelegate
from filter_template.filter_template_item_view_context_menu_delegate_factory import \
	FilterTemplateItemViewContextMenuDelegateFactory
from filter_template.filter_template_item_view_delegate import ImmutableFilterTemplateTreeViewDelegate
from filter_template.filter_template_item_viewl_delegate_factory import FilterTemplateItemViewDelegateFactory

I = DeepableQModelIndex
M = DeepableTreeModel
V = DeepableTreeView


class HSVManualThresholdFilterContextMenuDelegateFactory(FilterTemplateItemViewContextMenuDelegateFactory):

	def _create_delegate(self, index: I, view: V, filter_data) -> typing.Optional[
		AbstractItemViewContextMenuDelegate[I, V]]:
		if not index.isValid():
			return HSVManualThresholdFilterContextMenuDelegate(view)
		elif isinstance(filter_data, HSVManualThresholdFilterData):
			return HSVManualThresholdFilterContextMenuDelegate(view)
		else:
			return None


class HSVManualThresholdFilterContextMenuDelegate(FilterTemplateItemViewContextMenuDelegate):

	def create_menu(self, index: I) -> typing.Optional[QMenu]:
		actions = []
		# Index may be invalid => no model for invalid index. So take model from view.
		model = self.view.model()
		if not index.isValid():
			add_action = self.create_add_action("Add HSV manual threshold filter", "hsv_manual_threshold_filter_",
												lambda k: HSVManualThresholdFilterData(k, k))
			actions.append(add_action)
			menu = create_menu("HSV threshold", actions)
			return menu
		else:
			return None

class HSVManualThresholdFilterModelDelegateFactory(FilterTemplateItemModelDelegateFactory):

	def _create(self, index: I, filter_data) -> typing.Optional[AbstractItemModelDelegate[I]]:
		if isinstance(filter_data, HSVManualThresholdFilterData):
			return HSVManualThresholdFilterModelDelegate()


class HSVManualThresholdFilterModelDelegate(FilterTemplateItemModelDelegate):

	def _is_index_readonly(self, index: I) -> bool:
		model = index.model()
		key, value = model.key(index), model.value(index)
		filter_key, last_key = first_last_keys(key)
		filter_data: FilterData = model[filter_key]
		# print(f"_is_index_readonly {last_key}")
		if index.column() == 1:
			if last_key in (HSVManualThresholdFilterData_.hsv_range):
				return False
			elif last_key in (HSVManualThresholdFilterData_.color_mode):
				return True
		return super()._is_index_readonly(index)


class HSVManualThresholdFilterViewDelegateFactory(FilterTemplateItemViewDelegateFactory):

	def _create(self, index: I, filter_data) -> typing.Optional[AbstractItemViewDelegate[I, M, V]]:
		if isinstance(filter_data, HSVManualThresholdFilterData):
			return HSVManualThresholdFilterTreeViewDelegate()


class HSVManualThresholdFilterTreeViewDelegate(ImmutableFilterTemplateTreeViewDelegate):

	def filter_data_type(self, filter_data_dict: dict) -> type:
		return HSVManualThresholdFilterData

	def _createEditor(self, parent: QWidget, option: QStyleOptionViewItem, index: I, key: str,
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

	def _sizeHint(self, option: QStyleOptionViewItem, index: I, key: str) -> QSize:
		*leading_keys, last_key = key.split('.')
		if last_key == HSVManualThresholdFilterData_.hsv_range:
			return QSize(100, 300)
		return super()._sizeHint(option, index, key)
