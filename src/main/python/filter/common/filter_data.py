from typing import List, Optional

from dataclasses import dataclass, field

from common.dataclass_utils import dataclass_fields


@dataclass
class ColumnDef:
	header: str
	value_path: str
	is_value_dict: bool = False


@dataclass
class CsvExportConfig:
	delimiter: str = ';'
	columns: List[ColumnDef] = field(default_factory=list)


@dataclass(frozen=True)
class FilterData:
	id: str
	label: str
	# filter_type: ClassVar[str] = 'filter_type'
	# filter_type: str = field(default='filter_type')
	filter_type: str = field(default='filter_type')
	csv_export_config: Optional[CsvExportConfig] = None


@dataclass_fields
class FilterData_(FilterData):
	pass