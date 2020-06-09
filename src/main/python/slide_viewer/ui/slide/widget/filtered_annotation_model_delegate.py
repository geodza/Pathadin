import typing
from typing import Any

from PyQt5.QtCore import Qt, QSize
from PyQt5.QtGui import QColor
from PyQt5.QtWidgets import QWidget, QStyleOptionViewItem

from common_qt.editor.dropdown import Dropdown, commit_close_after_dropdown_select
from common_qt.mvc.model.delegate.item_model_delegate import AbstractItemModelDelegate
from common_qt.mvc.view.delegate.abstract_item_view_delegate import AbstractItemViewDelegate, T
from deepable.core import first_last_keys
from deepable_qt.model.deepable_model_index import DeepableQModelIndex
from deepable_qt.model.deepable_tree_model import DeepableTreeModel
from deepable_qt.model.tree_view_config_deepable_tree_model_delegate import TreeViewConfigDeepableTreeModelDelegate
from deepable_qt.view.deepable_tree_view import DeepableTreeView
from annotation.model import AnnotationModel
from slide_viewer.ui.slide.widget.filter.filter_data_service import FilterDataService
from slide_viewer.ui.slide.widget.interface.annotation_pixmap_provider import AnnotationItemPixmapProvider

I = DeepableQModelIndex
M = DeepableTreeModel
V = DeepableTreeView


# def annotation_model_delegate_wrapper(method):
# 	@wraps(method)
# 	def _impl(self, *method_args, **method_kwargs):
# 		annotation_model_delegate: AbstractItemModelDelegate[T] = self.annotation_model_delegate
# 		delegate_method = getattr(annotation_model_delegate, method.__name__)
# 		method_output = delegate_method(*method_args, **method_kwargs)
# 		return method_output
#
# 	return _impl

class FilterAnnotationViewDelegate(AbstractItemViewDelegate[I, M, V]):

	def __init__(self, annotation_view_delegate: AbstractItemViewDelegate[I, M, V],
				 filter_data_service: FilterDataService):
		super().__init__()
		self.annotation_view_delegate = annotation_view_delegate
		self.filter_data_service = filter_data_service

	def createEditor(self, parent: QWidget, option: QStyleOptionViewItem, index: I) -> QWidget:
		if index.column() == 1:
			model = index.model()
			key, value = model.key(index), model.value(index)
			filter_key, last_key = first_last_keys(key)
			value = model.value(index)
			if last_key == 'filter_id':
				filter_items = self.filter_data_service.get_filter_items()
				# filter_item = next(fd for fd in filter_items if fd.id == value)
				dropdown = Dropdown(filter_items, value, parent, label_func=lambda fd: fd.label,
									value_func=lambda fd: fd.id)
				return commit_close_after_dropdown_select(self, dropdown)
		return self.annotation_view_delegate.createEditor(parent, option, index)

	def updateEditorGeometry(self, editor: QWidget, option: QStyleOptionViewItem, index: I) -> None:
		if isinstance(editor, Dropdown):
			super().updateEditorGeometry(editor, option, index)
			editor.showPopup()
		else:
			super().updateEditorGeometry(editor, option, index)

class FilteredAnnotationModelDelegate(TreeViewConfigDeepableTreeModelDelegate):

	def __init__(self, annotation_model_delegate: AbstractItemModelDelegate[I],
				 annotation_item_pixmap_provider: typing.Optional[AnnotationItemPixmapProvider]):
		self.annotation_model_delegate = annotation_model_delegate
		self.annotation_item_pixmap_provider = annotation_item_pixmap_provider

	def flags(self, index: I) -> Qt.ItemFlags:
		return self.annotation_model_delegate.flags(index)

	def setData(self, index: I, value: typing.Any, role: int = Qt.DisplayRole) -> bool:
		return self.annotation_model_delegate.setData(index, value, role)

	def data(self, index: I, role: int = Qt.DisplayRole) -> Any:
		if role == Qt.DecorationRole and index.column() == 0:
			model = index.model()
			key, value = model.key(index), model.value(index)
			first_key, last_key = first_last_keys(key)
			if last_key.startswith("#"):
				# return QColor("#FF0000")
				return QColor(last_key)
		# return QColor(value)

		model = index.model()
		value = model.value(index)
		# if role == Qt.SizeHintRole:
		# 	return QSize(100, 100)
		if index.column() == 0:
			# if isinstance(value, AnnotationModel) and role == Qt.SizeHintRole:
			# 	return QSize(64, 64)

			if isinstance(value, AnnotationModel) and value.filter_id and self.annotation_item_pixmap_provider:
				if role == Qt.DecorationRole:
					def dc():
						# TODO how to update?
						# model.dataChanged.emit(index, index, [Qt.DecorationRole])
						pass

					# model.layoutChanged.emit()
					# model.setData(index,self.annotation_item_pixmap_provider.get_pixmap(value.id,lambda :None)[1],Qt.SizeHintRole)
					# model.dataChanged.emit(index, index)
					level_pixmap = self.annotation_item_pixmap_provider.get_pixmap(value.id, dc)
					if level_pixmap:
						if role == Qt.DecorationRole:
							# index.model().
							size = index.data(Qt.SizeHintRole) or QSize(64, 64)
							return level_pixmap[1].scaled(size, Qt.KeepAspectRatio)
		# elif role == Qt.SizeHintRole:
		# 	return level_pixmap[1].size()

		return self.annotation_model_delegate.data(index, role)

# def on_data_changed(self, topLeft: T, bottomRight: T, roles: typing.Iterable[int]) -> None:
# 	print("index.data(Qt.SizeHintRole)", dd)
