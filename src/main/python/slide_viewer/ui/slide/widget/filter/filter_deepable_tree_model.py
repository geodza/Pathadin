from typing import Optional

from PyQt5.QtCore import QObject, QModelIndex

from deepable_qt.deepable_tree_model import DeepableTreeModel


@dataclass
class FilterDeepableTreeModel(DeepableTreeModel):

	def __post_init__(self, parent_: Optional[QObject]):
		super().__post_init__(parent_)

	def _is_index_readonly(self, index: QModelIndex) -> bool:
		key, value = self.model.key(index), self.model.value(index)
		filter_id = toplevel_key(key)
		filter_data: FilterData = self.model[filter_id]
		key = key.split('.')[-1]
		key, value = self.model.key(index), self.model.value(index)
		filter_id = toplevel_key(key)
		filter_data: FilterData = self.model[filter_id]
		key = key.split('.')[-1]
		if key == FilterData_.filter_type:
			return True
		elif key == FilterData_.realtime:
			return True
		elif isinstance(filter_data, ThresholdFilterData):
			if key == ThresholdFilterData_.threshold_type:
				return True
			elif isinstance(filter_data, ManualThresholdFilterData):
				if key == ManualThresholdFilterData_.color_mode:
					return True
				elif isinstance(filter_data, HSVManualThresholdFilterData):
					if key == HSVManualThresholdFilterData_.hsv_range:
						return True
					else:
						raise ValueError(f"Unknown key {key} for filter {filter_data}")
				elif isinstance(filter_data, GrayManualThresholdFilterData):
					# self.sizeHintChanged.emit(index.sibling(index.row() + 1, index.column()))
					if key == GrayManualThresholdFilterData_.gray_range:
						return True
					else:
						return super().createEditor(parent, option, index)
				# raise ValueError(f"Unknown key {key} for filter {filter_data}")
				else:
					raise ValueError(f"Unknown key {key} for filter {filter_data}")
			elif isinstance(filter_data, SkimageAutoThresholdFilterData):
				if key == SkimageAutoThresholdFilterData_.skimage_threshold_type:
					return True
				else:
					if isinstance(filter_data, SkimageMeanThresholdFilterData):
						raise ValueError(f"Unknown key {key} for filter {filter_data}")
					elif isinstance(filter_data, SkimageMinimumThresholdFilterData):
						if key in (SkimageMinimumThresholdParams_.max_iter, SkimageMinimumThresholdParams_.nbins):
							return True
						else:
							raise ValueError(f"Unknown key {key} for filter {filter_data}")
					else:
						raise ValueError(f"Unknown key {key} for filter {filter_data}")
		elif isinstance(filter_data, KMeansFilterData):
			if key == KMeansParams_.init:
				return True
			elif key in (KMeansParams_.max_iter, KMeansParams_.n_clusters,
						 KMeansParams_.n_init, KMeansParams_.precompute_distances,
						 KMeansParams_.random_state, KMeansParams_.tol):
				return True
			else:
				raise ValueError(f"Unknown key {key} for filter {filter_data}")
		elif isinstance(filter_data, NucleiFilterData):
			keys = deep_keys(NucleiParams)
			if key in keys:
				return True
			else:
				raise ValueError(f"Unknown key {key} for filter {filter_data}")
		elif isinstance(filter_data, PositivePixelCountFilterData):
			keys = deep_keys(PositivePixelCountParams)
			if key in keys:
				return True
			else:
				raise ValueError(f"Unknown key {key} for filter {filter_data}")
		elif isinstance(filter_data, KerasModelFilterData):
			keys = deep_keys(KerasModelParams)
			if key == KerasModelParams_.model_path:
				return True
			elif key in keys:
				return True
			else:
				raise ValueError(f"Unknown key {key} for filter {filter_data}")
		# else:
		# 	raise ValueError(f"Unknown filter type {filter_data}")

		return super()._is_index_readonly(index)



