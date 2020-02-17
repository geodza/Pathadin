from typing import Optional

import numpy as np
from dataclasses import dataclass


@dataclass
class NdImageData:
    ndimg: np.ndarray
    color_mode: str
    bool_mask_ndimg: Optional[np.ndarray] = None