from typing import List, Dict, Tuple

from PyQt5.QtCore import QObject, pyqtBoundSignal, pyqtSignal

from annotation.model import AnnotationModel, AnnotationStats
from common.log_utils import log
from common_qt.abcq_meta import ABCQMeta
from deepable.core import toplevel_keys
from deepable_qt.model.deepable_tree_model import DeepableTreeModel
from filter.common.filter_model import FilterResults
from slide_viewer.ui.slide.widget.annotation.annotation_service import AnnotationService

ituple = Tuple[int, int]


class DeepableAnnotationService(QObject, AnnotationService, metaclass=ABCQMeta):
	# It is important to update tree annotations_tree_model from main gui thread and not from thread-pool task thread
	# It is important to update data of annotations_tree_model only through annotations_tree_model interface
	# We copy annotation, edit it and finally change annotations_tree_model through annotations_tree_model interface

	added = pyqtSignal(AnnotationModel)
	edited = pyqtSignal(str, AnnotationModel)
	deleted = pyqtSignal(list)
	selected = pyqtSignal(list)

	def __init__(self, root: DeepableTreeModel) -> None:
		self.root = root
		self.annotation_label_template: str = 'annotation_{}'
		self.root.keysRemoved.connect(self.__on_removed)
		self.root.keysChanged.connect(self.__on_changed)
		self.root.keysInserted.connect(self.__on_added)
		super().__init__()

	def get_first_point(self, id_: str) -> ituple:
		return self.get(id_).geometry.points[0]

	def add_point(self, id_: str, p: ituple) -> None:
		model = self.get(id_).copy(deep=True)
		model.geometry.points.append(p)
		self.root[id_] = model

	def add(self, model: AnnotationModel) -> AnnotationModel:
		model.id = self.get_next_id()
		model.label = self.annotation_label_template.format(model.id)
		self.root[model.id] = model
		return model

	def add_copy_or_edit_with_copy(self, model: AnnotationModel) -> AnnotationModel:
		# When syncing annotations between views and active view creates
		# annotation with id new for active view but already existing for another views
		# this new annotation will overwrite annotations with its id in another views.
		# Another option is to maintain global self.get_next_id() like some global sequence.
		model_copy = model.copy(deep=True)
		self.root[model_copy.id] = model_copy
		return model_copy

	def add_or_edit(self, id_: str, model: AnnotationModel) -> AnnotationModel:
		self.root[id_] = model
		return self.get(id_)

	def add_or_edit_with_copy(self, id_: str, model: AnnotationModel) -> AnnotationModel:
		# with slot_disconnected(self.root.objectsChanged, self.__on_changed):
		model_copy = model.copy(deep=True)
		self.root[id_] = model_copy
		# self.edited_signal().emit(id_, model_copy)
		return model_copy

	def add_or_edit_with_copy_without_filter(self, id_: str, model: AnnotationModel) -> AnnotationModel:
		# with slot_disconnected(self.root.objectsChanged, self.__on_changed):
		model_copy = model.copy(deep=True)
		model_copy.filter_results = None
		model_copy.filter_id = None
		model_copy.filter_level = None
		original_model = self.get(id_)
		if original_model:
			original_model_dict = original_model.dict()
			model_copy_dict = model_copy.dict(exclude={'filter_results', 'filter_id', 'filter_level'})
			original_model_dict.update(model_copy_dict)
			merged_model = AnnotationModel.parse_obj(original_model_dict)
		else:
			merged_model = model_copy
		self.root[id_] = merged_model
		# self.edited_signal().emit(id_, merged_model)
		return merged_model

	def edit_origin_point(self, id_: str, p: ituple) -> None:
		model = self.get(id_).copy(deep=True)
		# model.geometry.origin_point = p
		# self.root[id_] = model
		self.root[f'{id_}.geometry.origin_point'] = p

	def edit_last_point(self, id_: str, p: ituple) -> None:
		model = self.get(id_)
		# model_copy = model.copy(deep=True)
		# model_copy.geometry.points[-1] = p
		# self.root[id_] = model_copy
		new_points = list(model.geometry.points)
		new_points[-1]=p
		self.root[f'{id_}.geometry.points'] = new_points

	@log()
	def edit_filter_results(self, id_: str, filter_results: FilterResults) -> None:
		self.root[f'{id_}.filter_results'] = filter_results

	def edit_stats(self, id_: str, stats: AnnotationStats) -> None:
		self.root[f'{id_}.stats'] = stats

	def get(self, id_: str) -> AnnotationModel:
		return self.root[id_]

	def has(self, id_: str) -> bool:
		return id_ in self.root

	def get_dict(self) -> Dict[str, AnnotationModel]:
		return {id_: self.root[id_] for id_ in self.root}

	def has(self, id_: str) -> bool:
		return id_ in self.root

	def delete(self, ids: List[str]) -> None:
		for id_ in ids:
			del self.root[id_]

	def delete_if_exist(self, ids: List[str]) -> None:
		for id_ in ids:
			if self.has(id_):
				del self.root[id_]

	def delete_all(self) -> None:
		for key in self.root:
			del self.root[key]

	def added_signal(self) -> pyqtBoundSignal(AnnotationModel):
		return self.added

	def edited_signal(self) -> pyqtBoundSignal(str, AnnotationModel):
		return self.edited

	def deleted_signal(self) -> pyqtBoundSignal(list):
		return self.deleted

	def get_next_id(self) -> str:
		try:
			int_ids = [int(id_) for id_ in self.root if id_.isdigit()]
			next_id = max(int_ids) + 1 if int_ids else 1
			return str(next_id)
		except:
			next_id = len(self.root) + 1
			return str(next_id)

	def __on_removed(self, keys: List[str]):
		selected_toplevel_keys = toplevel_keys(keys) & set(keys)
		self.deleted_signal().emit(list(selected_toplevel_keys))

	def __on_added(self, keys: List[str]):
		for toplevel_key in toplevel_keys(keys) & set(keys):
			# print("on_added", toplevel_key)
			self.added_signal().emit(self.get(toplevel_key))

	def __on_changed(self, keys: List[str]):
		for toplevel_key in toplevel_keys(keys):
			id_ = toplevel_key
			# print(f"keys: {keys} top_level_key: {toplevel_key} onChanged")
			model = self.get(id_)
			# if self.stats_processor and False:
			# 	stats = self.stats_processor.calc_stats(model)
			# 	stats_dict = stats.dict() if stats else None
			# 	old_stats_dict = model.stats.dict() if model.stats else None
			# 	stats = self.stats_processor.calc_stats(model)
			# 	if stats_dict == old_stats_dict:
			# 		self.edited_signal().emit(id_, model)
			# 	else:
			# 		self.root[f'{id_}.stats'] = stats
			# 		# self.edit_stats(id_, stats)
			# 		# self.add_or_edit(toplevel_key, model)
			# else:
			self.edited_signal().emit(id_, model)
