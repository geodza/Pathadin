import typing

from deepable_qt.model.deepable_tree_model import DeepableTreeModel
from filter.common.filter_model import FilterData


class FilterDataService:

	def __init__(self, root: DeepableTreeModel) -> None:
		super().__init__()
		self.root = root

	# self.root.keysRemoved.connect(self.__on_removed)
	# self.root.keysChanged.connect(self.__on_changed)
	# self.root.keysInserted.connect(self.__on_added)

	def get_filter_item(self, filter_id: str) -> typing.Optional[FilterData]:
		model = self.root
		for k in model:
			filter_data: FilterData = model[k]
			if filter_data.id == filter_id:
				return filter_data
		return None

	def get_filter_items(self) -> typing.List[FilterData]:
		model = self.root
		filters = []
		for k in model:
			filter_data: FilterData = model[k]
			filters.append(filter_data)
		return filters
