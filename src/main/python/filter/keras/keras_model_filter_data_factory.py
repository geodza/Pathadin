from dacite import from_dict

from filter.common.filter_data_factory import FilterDataFactory, F, FilterDataFactoryFactory
from filter.keras.keras_model_filter_model import KerasModelFilterData


class KerasModelFilterDataFactoryFactory(FilterDataFactoryFactory):

	def create_factory(self, filter_type: str) -> FilterDataFactory[F]:
		if filter_type == "keras_model":
			return KerasModelFilterDataFactory()


class KerasModelFilterDataFactory(FilterDataFactory):

	def create_filter_data(self, filter_type: str, filter_data_dict: dict) -> F:
		if filter_type == "keras_model":
			return from_dict(KerasModelFilterData, filter_data_dict)
