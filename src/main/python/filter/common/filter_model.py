from typing import Optional, Any, Dict, List

import numpy as np
from PyQt5.QtGui import QImage
from dataclasses import dataclass, field
from pydantic import BaseModel

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


# @dataclass(frozen=True)
class FilterResults(BaseModel):
	# Custom classes inside attributes field are forbidden to allow simple serialization/deserialization inside AnnotationModel.
	# For the same reason subclassing FilterResults is forbidden.
	text: Optional[str]
	attributes: Optional[Dict[str, Any]]

	def __init__(self, text: Optional[str], attributes: Optional[Dict[str, Any]]):
		super().__init__(text=text, attributes=attributes)


@dataclass
class FilterOutput:
	# Common workflow of a filter:
	# 1) openslide reads pilimage
	# 2) convert pilimage to numpy array
	# 3) filter works with numpy array and outputs numpy array
	# 4) convert numpy array to QImage
	# 5) convert QImage to QPixmap
	# 6) put QPixmap to QPixmapCache
	# This workflow determines type for filter output image.
	# FilterResults will be generated in task-threads.
	# It is better to push as much work as possible from main GUI-thread to task-threads.
	# But QPixmap(and QBitmap) can be created only in main GUI-thread.
	# So the last available type of filter output image for task-thread is QImage.
	img: QImage
	bool_mask_ndimg: Optional[np.ndarray]
	results: FilterResults
