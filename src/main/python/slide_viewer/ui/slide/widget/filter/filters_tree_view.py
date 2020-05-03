import typing
from PyQt5.QtCore import Qt, QPoint, QModelIndex
from PyQt5.QtWidgets import QWidget, QMenu

from common_qt.my_action import MyAction
from deepable.core import deep_supports_key_add
from deepable_qt.context_menu_factory2 import DeepableTreeViewActionsFactory
from deepable_qt.deepable_tree_model import DeepableTreeModel
from deepable_qt.deepable_tree_view import DeepableTreeView
from img.filter.manual_threshold import GrayManualThresholdFilterData
from slide_viewer.ui.slide.widget.filter.filter_tree_view_delegate import FilterTreeViewDelegate


def create_filters_tree_view(parent_: typing.Optional[QWidget], model: DeepableTreeModel) -> DeepableTreeView:
	filters_tree_view = DeepableTreeView(parent_, model_=model)
	filters_tree_view.setContextMenuPolicy(Qt.CustomContextMenu)
	filters_tree_view.customContextMenuRequested.connect(create_filters_tree_view_context_menu(filters_tree_view))
	filters_tree_view.setItemDelegate(FilterTreeViewDelegate(model))
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
			actions.append(factory.duplicate())

		menu = QMenu()
		for a in actions:
			a.setParent(menu)
			menu.addAction(a)

		menu.exec_(view.viewport().mapToGlobal(position))

	return on_filter_context_menu
