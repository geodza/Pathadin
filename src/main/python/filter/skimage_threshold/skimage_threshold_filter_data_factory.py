from dacite import from_dict

from filter.common.filter_data_factory import FilterDataFactory, F, FilterDataFactoryFactory
from filter.skimage_threshold.skimage_threshold_filter_model import SkimageThresholdType, \
	SkimageMeanThresholdFilterData, SkimageMinimumThresholdFilterData


class SkimageThresholdFilterDataFactoryFactory(FilterDataFactoryFactory):

	def create_factory(self, filter_type: str) -> FilterDataFactory[F]:
		if filter_type in (t for t in SkimageThresholdType):
			return SkimageThresholdFilterDataFactory()


class SkimageThresholdFilterDataFactory(FilterDataFactory):

	def create_filter_data(self, filter_type: str, filter_data_dict: dict) -> F:
		skimage_threshold_type = filter_data_dict['skimage_threshold_type']
		if skimage_threshold_type == SkimageThresholdType.threshold_mean:
			return from_dict(SkimageMeanThresholdFilterData, filter_data_dict)
		elif skimage_threshold_type == SkimageThresholdType.threshold_minimum:
			return from_dict(SkimageMinimumThresholdFilterData, filter_data_dict)
