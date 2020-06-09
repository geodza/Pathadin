import csv
import json
import typing
from collections import OrderedDict

from PyQt5.QtCore import Qt, QPoint, QModelIndex
from PyQt5.QtWidgets import QWidget, QMenu

from annotation.model import AnnotationModel
from common_qt.action.my_action import MyAction
from common_qt.action.select_json_file_action import show_select_file_dialog, csv_mime_types
from deepable.convert import DeepableJSONEncoder
from deepable.core import deep_supports_key_add, is_immutable, deep_local_key, deep_get
from deepable_qt.context_menu_factory2 import DeepableTreeViewActionsFactory
from deepable_qt.model.deepable_tree_model import DeepableTreeModel
from deepable_qt.view.deepable_tree_view import DeepableTreeView
from slide_viewer.ui.slide.widget.filter.filter_data_service import FilterDataService


def create_annotations_tree_view(parent_: typing.Optional[QWidget], model: DeepableTreeModel,
								 filter_data_service: FilterDataService) -> DeepableTreeView:
	tree_view = DeepableTreeView(parent_)
	tree_view.setModel(model)
	tree_view.setContextMenuPolicy(Qt.CustomContextMenu)
	tree_view.customContextMenuRequested.connect(
		create_annotations_tree_view_context_menu(tree_view, filter_data_service))
	return tree_view


def can_be_restored_from_json_by_default(obj: typing.Any) -> bool:
	# We do not use isinstance because isinstance would allow EnumA(str, Enum) and other types from hierarchy we cant restore back from json by default
	# TODO add dict, list support if they do not have nested user-defined objects so that they can be restored from json by default.
	return type(obj) in (str, int, float, bool)


def create_annotations_tree_view_context_menu(view: DeepableTreeView, filter_data_service: FilterDataService):
	def on_context_menu(position: QPoint):
		if not view.model().rowCount():
			return
		if not view.indexAt(position).isValid():
			view.setCurrentIndex(QModelIndex())

		factory = DeepableTreeViewActionsFactory(view)
		actions = []

		def is_top_level(index: QModelIndex) -> bool:
			return not index.parent().isValid()

		if all(deep_supports_key_add(factory.model.value(i)) for i in factory.indexes):
			actions.append(factory.add_attr())

		if all(is_top_level(i) or deep_supports_key_add(factory.model.value(i.parent())) for i in factory.indexes):
			actions.append(factory.delete())

		if all(is_top_level(i) or deep_supports_key_add(factory.model.value(i.parent())) for i in factory.indexes):
			actions.append(factory.duplicate())

		if all(is_top_level(i) for i in factory.indexes):
			def on_filter_results_csv_export():
				filter_results_csv_export_configs = OrderedDict()
				annotation_models = OrderedDict()
				for i in factory.indexes:
					if i.column() == 0:
						key, value = view.model().key(i), view.model().value(i)
						annotation_model: AnnotationModel = value
						if annotation_model.filter_id:
							filter_data = filter_data_service.get_filter_item(annotation_model.filter_id)
							if filter_data.csv_export_config:
								filter_results_csv_export_configs[key] = filter_data.csv_export_config
								annotation_models[key] = annotation_model

				rows = []
				headers = OrderedDict()
				for key in annotation_models:
					annotation_model = annotation_models[key]
					config = filter_results_csv_export_configs[key]
					row = OrderedDict()
					for column in config.columns:
						column_value = deep_get(annotation_model, column.value_path)
						if column.is_value_dict:
							for i, k in enumerate(column_value):
								key_header = f'{column.header}.{i}.key'
								row[key_header] = k
								headers[key_header] = key_header
								value_header = f'{column.header}.{i}.value'
								row[value_header] = column_value[k]
								headers[value_header] = value_header
						else:
							header = f'{column.header}'
							row[header] = column_value
							headers[header] = header
					rows.append(row)

				if not rows:
					return
				delimiter = next(cfg.delimiter for cfg in filter_results_csv_export_configs.values())
				# print(rows)
				file = show_select_file_dialog(view, save=True, default_file_name='filter_results.csv',
											   mime_types=csv_mime_types())
				if file:
					with open(file, 'w') as csvfile:
						fieldnames = list(headers)
						writer = csv.DictWriter(csvfile, fieldnames=fieldnames, dialect='excel', delimiter=delimiter)
						writer.writeheader()
						for row in rows:
							writer.writerow(row)

			actions.append(
				MyAction(f"Export filter results of {factory.mode} to csv ", action_func=on_filter_results_csv_export))

		if factory.current_index is not None:
			actions.append(factory.separator())

			current_key = factory.model.key(factory.current_index)
			# target_values = [factory.model.value(i) for i in view.selectedIndexes()]
			# print(current_key)
			# print(
			# 	[[is_deepable(v), not is_immutable(v), deep_contains(v, source_local_key), deep_supports_key_add(v)] for v in
			# 	 target_values])
			# print("target_values", target_values)
			current_local_key = deep_local_key(current_key)
			# print(factory.update_indexes, factory.current_index)
			if all(is_top_level(i) for i in factory.update_indexes) \
					and current_local_key not in ("id", "stats", "filter_results"):
				actions.append(factory.update())

			# if all(is_deepable(v) and not is_immutable(v) and (
			# 		deep_contains(v, source_local_path[0]) or deep_supports_key_add(v))
			# 	   for v in target_values):
			# 	actions.append(factory.update())

			if is_top_level(factory.current_index):
				# Support editing as json for complex(possibly nested) objects that we know how to restore back from json.
				actions.append(factory.separator())
				actions.append(factory.edit_as_json(
					lambda key, value: json.dumps(value, indent=2, cls=DeepableJSONEncoder),
					lambda key, value_json: AnnotationModel.parse_raw(value_json)
				))
			else:
				# Support editing as json for primitive (not nested) types
				current_value = factory.model.value(factory.current_index)
				current_value_parent = factory.model.value(factory.current_index.parent())
				if can_be_restored_from_json_by_default(current_value) and not is_immutable(
						current_value_parent):
					actions.append(factory.separator())
					actions.append(factory.edit_as_json(
						lambda key, value: json.dumps(value, indent=2, cls=DeepableJSONEncoder),
						lambda key, value_json: json.loads(value_json)
					))

		menu = QMenu()
		for a in actions:
			a.setParent(menu)
			menu.addAction(a)

		menu.exec_(view.viewport().mapToGlobal(position))

	return on_context_menu
