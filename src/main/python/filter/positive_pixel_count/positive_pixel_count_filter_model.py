from typing import Optional

from dataclasses import field, dataclass
from histomicstk.segmentation import positive_pixel_count as ppc

from common.dataclass_utils import dataclass_fields
from filter.common.filter_data import ColumnDef, CsvExportConfig, FilterData


@dataclass(frozen=True)
class PositivePixelCountParams:
	# params: ppc.Parameters = default_ppc_params()
	hue_value: float = 0.05
	hue_width: float = 0.15
	saturation_minimum: float = 0.05
	intensity_upper_limit: float = 0.95
	intensity_weak_threshold: float = 0.65
	intensity_strong_threshold: float = 0.35
	intensity_lower_limit: float = 0.05


def default_ppc_csv_export_config():
	# return None
	ppc_columns = [ColumnDef(f, f'filter_results.attributes.ppc_output.{f}') for f in ppc.Output._fields]
	columns = [
		ColumnDef('annotation_id', 'id'),
		ColumnDef('annotation_label', 'label'),
		*ppc_columns
	]
	return CsvExportConfig(columns=columns)


@dataclass(frozen=True)
class PositivePixelCountFilterData(FilterData):
	csv_export_config: Optional[CsvExportConfig] = field(default_factory=default_ppc_csv_export_config)
	# filter_type: ClassVar[str] = 'positive_pixel_count'
	filter_type: str = field(default='positive_pixel_count')
	positive_pixel_count_params: PositivePixelCountParams = field(default_factory=PositivePixelCountParams)


@dataclass_fields
class PositivePixelCountFilterData_(PositivePixelCountFilterData):
	pass
