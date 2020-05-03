import typing
from PyQt5.QtCore import Qt, QPoint, QModelIndex
from PyQt5.QtWidgets import QWidget, QMenu

from common_qt.my_action import MyAction
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

        def on_reset():
            view.model().beginResetModel()
            view.model().endResetModel()

        menu = QMenu()
        MyAction("Add filter", menu, on_add)
        MyAction(f"Reset model", menu, on_reset)

        menu.exec_(view.viewport().mapToGlobal(position))

    return on_filter_context_menu