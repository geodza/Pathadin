from typing import Dict, ClassVar

from dataclasses import field, dataclass

from common.dataclass_utils import dataclass_fields
from filter.common.filter_data import ColumnDef, CsvExportConfig, FilterData


def default_stain_color_map():
	return {
		'hematoxylin': [0.65, 0.70, 0.29],
		'eosin': [0.07, 0.99, 0.11],
		'dab': [0.27, 0.57, 0.78],
		'null': [0.0, 0.0, 0.0]
	}


@dataclass(frozen=True)
class NucleiParams:
	stain_color_map: Dict[str, list] = field(default_factory=default_stain_color_map)  # specify stains of input image
	stain_1: str = 'hematoxylin'  # nuclei stain
	stain_2: str = 'eosin'  # cytoplasm stain
	stain_3: str = 'null'  # set to null of input contains only two stains
	foreground_threshold: int = 60
	min_radius: int = 10
	max_radius: int = 15
	local_max_search_radius: float = 10.0
	min_nucleus_area: int = 80

def default_nuclei_csv_export_config():
	columns = [
		ColumnDef('annotation_id', 'id'),
		ColumnDef('annotation_label', 'label'),
		ColumnDef('nuclei_count', 'filter_results.attributes.nuclei_count')
	]
	return CsvExportConfig(columns=columns)

@dataclass(frozen=True)
class NucleiFilterData(FilterData):
	csv_export_config: CsvExportConfig = field(default_factory=default_nuclei_csv_export_config)
	# filter_type: ClassVar[str] = 'nuclei'
	filter_type: str = field(default='nuclei')
	nuclei_params: NucleiParams = field(default_factory=NucleiParams)


@dataclass_fields
class NucleiFilterData_(NucleiFilterData):
	pass

