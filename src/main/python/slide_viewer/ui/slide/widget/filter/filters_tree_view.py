import typing
from collections import OrderedDict

from PyQt5.QtCore import Qt, QPoint, QModelIndex
from PyQt5.QtWidgets import QWidget, QMenu

from common_qt.action.my_action import MyAction
from common_qt.mvc.model.delegate.composite_item_model_delegate import CompositeAbstractItemModelDelegate
from common_qt.mvc.view.delegate.composite_item_view_delegate import CompositeItemViewDelegate
from common_qt.mvc.view.delegate.factory.standard_item_view_delegate_factory import StandardItemViewDelegateFactory
from common_qt.mvc.view.delegate.styled_item_view_delegate import QStyledItemViewDelegate
from deepable.core import deep_supports_key_add
from deepable_qt.context_menu_factory2 import DeepableTreeViewActionsFactory
from deepable_qt.model.deepable_tree_model import DeepableTreeModel
from deepable_qt.model.tree_view_config_deepable_tree_model_delegate import \
	TreeViewConfigDeepableTreeModelDelegateFactory
from deepable_qt.view.deepable_tree_view import DeepableTreeView
from img.filter.manual_threshold import GrayManualThresholdFilterData

from slide_viewer.ui.slide.widget.filter.plugin import load_filter_plugins


def create_filters_tree_model(filters: OrderedDict):
	model_delegates = []
	for filter_plugin in load_filter_plugins():
		model_delegates.append(filter_plugin.itemModelDelegateFactory())
	model_delegates.append(TreeViewConfigDeepableTreeModelDelegateFactory())
	model_delegate = CompositeAbstractItemModelDelegate(model_delegates)
	# model_delegate = CompositeAbstractItemModelDelegate([
	# 	GrayManualThresholdFilterModelDelegateFactory(),
	# 	HSVManualThresholdFilterModelDelegateFactory(),
	# 	TreeViewConfigDeepableTreeModelDelegateFactory()
	# ])
	filters_model = DeepableTreeModel(_root=filters, _modelDelegate=model_delegate)
	return filters_model


def create_filters_tree_view(parent_: typing.Optional[QWidget], model: DeepableTreeModel) -> DeepableTreeView:
	filters_tree_view = DeepableTreeView(parent_)
	filters_tree_view.setModel(model)
	filters_tree_view.setContextMenuPolicy(Qt.CustomContextMenu)
	filters_tree_view.customContextMenuRequested.connect(create_filters_tree_view_context_menu(filters_tree_view))
	# filters_tree_view.setItemDelegate(FilterTreeViewDelegate())
	view_delegates=[]
	for filter_plugin in load_filter_plugins():
		view_delegates.append(filter_plugin.itemViewDelegateFactory())
	view_delegates.append(StandardItemViewDelegateFactory())
	view_delegate=QStyledItemViewDelegate(CompositeItemViewDelegate(view_delegates))
	filters_tree_view.setItemDelegate(view_delegate)
	return filters_tree_view


def create_filters_tree_view_context_menu(view: DeepableTreeView):
	def on_filter_context_menu(position: QPoint):
		if not view.model().rowCount():
			return
		if not view.indexAt(position).isValid():
			view.setCurrentIndex(QModelIndex())

		def on_add():
			last_filted_id = len(view.model())
			new_filter_id = str(last_filted_id + 1)
			view.model()[new_filter_id] = GrayManualThresholdFilterData(new_filter_id)

		actions = []
		actions.append(MyAction("Add filter", action_func=on_add))
		factory = DeepableTreeViewActionsFactory(view)

		def is_top_level(index: QModelIndex) -> bool:
			return not index.parent().isValid()

		if all(is_top_level(i) or deep_supports_key_add(factory.model.value(i.parent())) for i in factory.indexes):
			actions.append(factory.delete())

		if all(is_top_level(i) or deep_supports_key_add(factory.model.value(i.parent())) for i in factory.indexes):
			actions.append(factory.duplicate())

		menu = QMenu()
		for a in actions:
			a.setParent(menu)
			menu.addAction(a)

		menu.exec_(view.viewport().mapToGlobal(position))

	return on_filter_context_menu
