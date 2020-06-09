import typing
from abc import ABC

from PyQt5.QtWidgets import QAction

from common_qt.mvc.view.delegate.abstract_item_view_context_menu_delegate import AbstractItemViewContextMenuDelegate
from deepable_qt.model.deepable_model_index import DeepableQModelIndex
from deepable_qt.model.deepable_tree_model import DeepableTreeModel
from deepable_qt.view.deepable_tree_view import DeepableTreeView
from filter.common.filter_model import FilterData

I = DeepableQModelIndex
M = DeepableTreeModel
V = DeepableTreeView
F = typing.TypeVar('F', bound=FilterData)


class FilterTemplateItemViewContextMenuDelegate(AbstractItemViewContextMenuDelegate[I, V], ABC):

	def create_add_action(self, title: str, key_prefix: str, filter_data_factory: typing.Callable[[str], F]) -> QAction:
		model = self.view.model()

		def on_add(checked: bool):
			rownum = len(model) + 1
			new_key = key_prefix + f"{rownum}"
			while new_key in model:
				rownum += 1
				new_key = key_prefix + f"{rownum}"
			filter_data = filter_data_factory(new_key)
			model[str(rownum)] = filter_data

			# model[new_key] = filter_data

		add_action = QAction(title)
		add_action.triggered.connect(on_add)
		return add_action

	# def create_add_column_action(self, title: str, index:I) -> typing.Optional[QAction]:
	# 	model = self.view.model()
	# 	filter_data: FilterData = model.value(index)
	# 	if filter_data.csv_export_config:
	# 		def on_add(checked: bool):
	#
	#
	# 			# model[new_key] = filter_data
	#
	# 		add_action = QAction(title)
	# 		add_action.triggered.connect(on_add)
	# 		return add_action
	# 	else:
	# 		return None
