from typing import Optional

import numpy as np
from PyQt5.QtGui import QImage
from dataclasses import dataclass

from filter.common.filter_results import FilterResults


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
