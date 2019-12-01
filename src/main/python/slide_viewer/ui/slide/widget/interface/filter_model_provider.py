from abc import ABC, abstractmethod

from slide_viewer.ui.model.filter.base_filter import FilterData


class FilterModelProvider(ABC):

    @abstractmethod
    def get_filter_model(self, filter_id: str) -> FilterData:
        pass
