import typing

from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QWidget, QMenu, QAction
from dataclasses import asdict

from common import json_utils
from common_qt.action.my_menu import create_menu
from common_qt.action.select_json_file_action import show_select_file_dialog, json_mime_types
from common_qt.mvc.model.delegate.composite_item_model_delegate import CompositeAbstractItemModelDelegate
from common_qt.mvc.view.delegate.abstract_item_view_context_menu_delegate import AbstractItemViewContextMenuDelegate, I
from common_qt.mvc.view.delegate.composite_item_view_context_menu_delegate import CompositeItemViewContextMenuDelegate
from common_qt.mvc.view.delegate.composite_item_view_delegate import CompositeItemViewDelegate
from common_qt.mvc.view.delegate.factory.abstract_item_view_context_menu_delegate_factory import \
	AbstractItemViewContextMenuDelegateFactory, V
from common_qt.mvc.view.delegate.factory.standard_item_view_delegate_factory import StandardItemViewDelegateFactory
from common_qt.mvc.view.delegate.styled_item_view_delegate import QStyledItemViewDelegate
from deepable.core import deep_keys, deep_get, Deepable, deep_set
from deepable_qt.model.deepable_tree_model import DeepableTreeModel
from deepable_qt.model.tree_view_config_deepable_tree_model_delegate import \
	TreeViewConfigDeepableTreeModelDelegateFactory
from deepable_qt.view.deepable_tree_view import DeepableTreeView
from filter.common.composite_filter_data_factory import CompositeFilterDataFactory
from filter.common.filter_data_factory import FilterDataFactory
from filter.filter_plugin import FilterPlugin
from filter_processor.composite_filter_processor import CompositeFilterProcessor
from filter_processor.filter_processor import FilterProcessor
from slide_viewer.ui.slide.widget.filter.plugin import load_filter_plugins


# I = DeepableQModelIndex
# V =QAbstractItemView


def create_filters_tree_model(filters: Deepable):
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


class FilterCommonContextMenuDelegateFactory(AbstractItemViewContextMenuDelegateFactory[I, V]):

	def __init__(self, filter_data_factory: FilterDataFactory):
		self.filter_data_factory = filter_data_factory

	def create_delegate(self, index: I, view: V) -> typing.Optional[AbstractItemViewContextMenuDelegate[I, V]]:
		if not index.isValid():
			return FilterCommonContextMenuDelegate(view, self.filter_data_factory)
		else:
			return None


class FilterCommonContextMenuDelegate(AbstractItemViewContextMenuDelegate[I, DeepableTreeView]):

	def __init__(self, view: V, filter_data_factory: FilterDataFactory):
		super().__init__(view)
		self.filter_data_factory = filter_data_factory

	def create_menu(self, index: I) -> QMenu:
		def on_export(_):
			model = self.view.model()
			root = model.get_root()
			# print("Export to json", json.dumps(root, default=self.json_encoder.default))
			# root_serializable=deep_to_di

			dicts = []
			for k in deep_keys(root):
				fd = deep_get(root, k)
				fdd = asdict(fd)
				deep_set(dicts, k, fdd)
			# dicts[k] = fdd
			# dicts_json = json.dumps(dicts)
			file_path = show_select_file_dialog(self.view, title='File to save filters', save=True,
												default_file_name='filters.json', mime_types=json_mime_types())
			if file_path:
				json_utils.write(file_path, dicts)

		def on_import(_):
			model = self.view.model()
			file_path = show_select_file_dialog(self.view, title='File to load filters', save=False,
												default_file_name='filters.json', mime_types=json_mime_types())
			if file_path:
				dicts2 = json_utils.read(file_path)
				root2 = []
				for k in deep_keys(dicts2):
					dict_ = deep_get(dicts2, k)
					fd = self.filter_data_factory.create_filter_data(dict_)
					deep_set(root2, k, fd)
				# root2[k] = fd
				model.set_root(root2)

		# print("Export to json", dicts_json)
		# dicts2 = json.loads(dicts_json)
		# root2 = {}
		# for k, dict_ in dicts2.items():
		# 	fd = self.filter_data_factory.create_filter_data(dict_)
		# 	root2[k] = fd
		# print(root2)
		# assert root == root2

		export_action = QAction("Export to json", triggered=on_export)
		import_action = QAction("Import from json", triggered=on_import)

		return create_menu("Export/import", [export_action, import_action])


def create_filters_tree_view(parent_: typing.Optional[QWidget], model: DeepableTreeModel,
							 filter_plugins: typing.List[FilterPlugin] = []) -> DeepableTreeView:
	filters_tree_view = DeepableTreeView(parent_)
	filters_tree_view.setModel(model)

	# filters_tree_view.setItemDelegate(FilterTreeViewDelegate())
	view_delegates = []
	view_context_menu_delegate_factories = []
	filter_data_factories = []
	for filter_plugin in filter_plugins:
		view_delegates.append(filter_plugin.itemViewDelegateFactory())
		view_context_menu_delegate_factories.append(filter_plugin.itemViewContextMenuDelegateFactory())
		filter_data_factories.append(filter_plugin.filterDataFactoryFactory())
	view_delegates.append(StandardItemViewDelegateFactory())
	view_delegate = QStyledItemViewDelegate(CompositeItemViewDelegate(view_delegates))
	filters_tree_view.setItemDelegate(view_delegate)

	filter_data_factory = CompositeFilterDataFactory(filter_data_factories)
	fmd = FilterCommonContextMenuDelegateFactory(filter_data_factory)
	view_context_menu_delegate_factories.append(fmd)

	view_context_menu_delegate = CompositeItemViewContextMenuDelegate(filters_tree_view,
																	  view_context_menu_delegate_factories)
	filters_tree_view.setContextMenuPolicy(Qt.CustomContextMenu)

	# filters_tree_view.customContextMenuRequested.connect(create_filters_tree_view_context_menu(filters_tree_view))
	def view_context_menu_delegate_keep_reference_hack(pos):
		view_context_menu_delegate.on_context_menu(pos)

	filters_tree_view.customContextMenuRequested.connect(view_context_menu_delegate_keep_reference_hack)

	return filters_tree_view


# def create_filters_tree_view_context_menu(view: DeepableTreeView):
# 	def on_filter_context_menu(position: QPoint):
# 		if not view.model().rowCount():
# 			return
# 		if not view.indexAt(position).isValid():
# 			view.setCurrentIndex(QModelIndex())
#
# 		def on_add():
# 			last_filted_id = len(view.model())
# 			new_filter_id = str(last_filted_id + 1)
# 			view.model()[new_filter_id] = GrayManualThresholdFilterData(new_filter_id)
#
# 		actions = []
# 		actions.append(MyAction("Add filter", action_func=on_add))
# 		factory = DeepableTreeViewActionsFactory(view)
#
# 		def is_top_level(index: QModelIndex) -> bool:
# 			return not index.parent().isValid()
#
# 		if all(is_top_level(i) or deep_supports_key_add(factory.model.value(i.parent())) for i in factory.indexes):
# 			actions.append(factory.delete())
#
# 		if all(is_top_level(i) or deep_supports_key_add(factory.model.value(i.parent())) for i in factory.indexes):
# 			actions.append(factory.duplicate())
#
# 		menu = QMenu()
# 		for a in actions:
# 			a.setParent(menu)
# 			menu.addAction(a)
#
# 		menu.exec_(view.viewport().mapToGlobal(position))
#
# 	return on_filter_context_menu
def create_filter_processor(filter_plugins: typing.List[FilterPlugin]) -> FilterProcessor:
	factories = [p.filterProcessorFactory() for p in filter_plugins]
	return CompositeFilterProcessor(factories)
