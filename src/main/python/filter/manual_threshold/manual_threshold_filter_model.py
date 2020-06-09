import typing

from dataclasses import dataclass, field

from common.dataclass_utils import dataclass_fields
from common_image.model.color_mode import ColorMode
from filter.common.filter_model import ColumnDef, CsvExportConfig
from filter.common.threshold_filter_model import ThresholdFilterData

def default_manual_threshold_csv_export_config():
	# return None
	columns = [
		ColumnDef('annotation_id', 'id'),
		ColumnDef('annotation_label', 'label'),
		ColumnDef('color', 'filter_results.attributes.histogram', True)
	]
	return  CsvExportConfig(columns=columns)

@dataclass(frozen=True)
class ManualThresholdFilterData(ThresholdFilterData):
	csv_export_config: typing.Optional[CsvExportConfig] = field(default_factory=default_manual_threshold_csv_export_config)
	# filter_type: ClassVar[str] = 'manual_threshold'
	filter_type: str = field(default='manual_threshold')
	color_mode: ColorMode = field(init=False)


@dataclass_fields
class ManualThresholdFilterData_(ManualThresholdFilterData):
	pass


@dataclass(frozen=True)
class GrayManualThresholdFilterData(ManualThresholdFilterData):
	color_mode: ColorMode = field(default=ColorMode.L)
	# color_mode: typing.ClassVar[ColorMode] = ColorMode.L
	gray_range: typing.Tuple[int, int] = (0, 255)


@dataclass_fields
class GrayManualThresholdFilterData_(GrayManualThresholdFilterData):
	pass


HSV = typing.Tuple[int, int, int]


@dataclass(frozen=True)
class HSVManualThresholdFilterData(ManualThresholdFilterData):
	color_mode: ColorMode = field(default=ColorMode.HSV)
	# color_mode: typing.ClassVar[ColorMode] = ColorMode.HSV
	hsv_range: typing.Tuple[HSV, HSV] = ((0, 0, 0), (255, 255, 255))


@dataclass_fields
class HSVManualThresholdFilterData_(HSVManualThresholdFilterData):
	pass