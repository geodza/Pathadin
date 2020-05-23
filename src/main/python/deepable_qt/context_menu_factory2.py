import copy
from typing import Tuple, List, Callable, Any

from PyQt5.QtCore import QModelIndex
from PyQt5.QtWidgets import QAbstractItemView, QAction

from common_qt.action.my_action import MyAction
from common_qt.dialog.edit_text_dialog import EditTextDialog
from common_qt.action.separator_action import SeparatorAction
from deepable.core import deep_local_path
from deepable_qt.view.deepable_tree_view import DeepableTreeView


def all_top_level_indexes(view: QAbstractItemView) -> List[QModelIndex]:
	return [view.model().index(row, 0) for row in range(view.model().rowCount())]


def get_update_mode_and_indexes(view: QAbstractItemView):
	current = view.currentIndex()
	selected = [i for i in view.selectionModel().selection().indexes() if i.column() == 0]
	# selected = [i for i in view.selectionModel().selection().indexes() if i.column() == 0]
	selected = [i for i in selected if not i.parent().isValid()]
	if len(selected) and not (len(selected) == 1 and current in selected):
		update_mode, update_indexes = "selected", list(selected)
	else:
		update_mode, update_indexes = "all", all_top_level_indexes(view)
	return update_mode, update_indexes


def get_mode_and_indexes(view: QAbstractItemView) -> Tuple[str, List[QModelIndex]]:
	current_index = view.currentIndex()
	selected_indexes = [i for i in view.selectionModel().selection().indexes() if i.column() == 0]
	if current_index.isValid() and view.selectionModel().isSelected(current_index):
		mode, indexes = "selected", list(selected_indexes)
	elif current_index.isValid():
		mode, indexes = "current", [current_index]
	else:
		mode, indexes = "all", all_top_level_indexes(view)
	parent_index_ids = set(id(i.parent()) for i in indexes)
	indexes = [i for i in indexes if id(i) not in parent_index_ids]
	return mode, indexes


class DeepableTreeViewActionsFactory:

	def __init__(self, view: DeepableTreeView) -> None:
		super().__init__()
		self.view = view
		self.mode, self.indexes = get_mode_and_indexes(view)
		self.current_number, self.current_index, self.update_mode, self.update_indexes = None, None, None, None
		if self.mode == 'current' or (self.mode == 'selected' and len(self.indexes) == 1):
			self.current_index = next(iter(self.indexes))
			#     self.current_index = self.model.index(self.current_number, 0)
			self.update_mode, self.update_indexes = get_update_mode_and_indexes(view)

	@property
	def model(self):
		return self.view.model()

	def separator(self) -> QAction:
		return SeparatorAction()

	def delete(self) -> QAction:
		mode, indexes, model = self.mode, self.indexes, self.model

		def f():
			for i in indexes:
				key = model.key(i)
				del model[key]

		return MyAction(f"Delete {mode}", action_func=f)

	def add_attr(self, new_attr_key_pattern: str = "{index}",
				 new_attr_value_factory: Callable[[], Any] = lambda: "") -> QAction:
		mode, indexes, model = self.mode, self.indexes, self.model

		def f():
			for i in indexes:
				key = model.key(i)
				index = model.rowCount(i)
				new_attr_local_key = new_attr_key_pattern.format_map({"index": index})
				new_attr_key = ".".join([key, new_attr_local_key])
				new_value = new_attr_value_factory()
				model[new_attr_key] = new_value


		return MyAction(f"Add new attr to {mode}", action_func=f)

	def duplicate(self, copy_key_pattern: str = "{key}_{index}",
				  copy_value_factory: Callable[[Any], Any] = lambda value: copy.deepcopy(value)) -> QAction:
		mode, indexes, model = self.mode, self.indexes, self.model

		def f():
			for i in indexes:
				key = model.key(i)
				index = model.rowCount(i.parent())
				copy_key = copy_key_pattern.format_map({"index": index, "key": key})
				value = model[key]
				copy_value = copy_value_factory(value)
				# copy_value = copy.deepcopy(value)
				# if 'id' in deep_keys(value):
				# 	deep_set(copy_value, 'id', copy_key)
				model[copy_key] = copy_value

		return MyAction(f"Duplicate {mode}", action_func=f)

	def update(self,
			   copy_value_factory: Callable[[Any], Any] = lambda source_value: copy.deepcopy(source_value)) -> QAction:
		mode, indexes, model, current_index, update_indexes, update_mode = \
			self.mode, self.indexes, self.model, self.current_index, self.update_indexes, self.update_mode

		# keys_to_ignore = set(['id', 'name'])

		def f():
			source_key, source_value = model.key(current_index), model.value(current_index)
			source_local_path = deep_local_path(source_key)
			for i in update_indexes:
				target_key = '.'.join([model.key(i)] + source_local_path)
				# target_value = model[target_key]
				try:
					source_value_copy = copy_value_factory(source_value)
					model[target_key] = source_value_copy
				except Exception as e:
					# Target object hasn't appropriate structure.
					# Try to update it with object in higher level.
					# This occurs when you try to copy a.b.c to a1 which hasn't b, so you need to copy b first.
					pass

		return MyAction(f"Update {update_mode} with current", action_func=f)

	def edit_as_json(self, to_json_converter: Callable[[str, Any], str],
					 from_json_converter: Callable[[str, str], Any]) -> QAction:
		mode, indexes, model, current_index = self.mode, self.indexes, self.model, self.current_index

		def f():
			key, value = model.key(current_index), model.value(current_index)
			obj_json = to_json_converter(key, value)

			dialog = EditTextDialog(obj_json)

			def on_edit_ok():
				new_obj_json = dialog.text_editor.toPlainText()
				new_obj = from_json_converter(key, new_obj_json)
				model[key] = new_obj

			dialog.accepted.connect(on_edit_ok)
			dialog.show()

		return MyAction(f"Edit {mode} as JSON", action_func=f)
