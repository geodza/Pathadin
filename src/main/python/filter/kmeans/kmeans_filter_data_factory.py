from dacite import from_dict

from filter.common.filter_data_factory import FilterDataFactory, F, FilterDataFactoryFactory
from filter.kmeans.kmeans_filter_model import KMeansFilterData


class KMeansFilterDataFactoryFactory(FilterDataFactoryFactory):

	def create_factory(self, filter_type: str) -> FilterDataFactory[F]:
		if filter_type == "kmeans":
			return KMeansFilterDataFactory()


class KMeansFilterDataFactory(FilterDataFactory):

	def create_filter_data(self, filter_type: str, filter_data_dict: dict) -> F:
		if filter_type == "kmeans":
			return from_dict(KMeansFilterData, filter_data_dict)
