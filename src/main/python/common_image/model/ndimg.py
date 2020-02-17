from typing import Optional

import numpy as np
from dataclasses import dataclass


@dataclass
class Ndimg:
    ndarray: np.ndarray
    color_mode: str
    bool_mask_ndarray: Optional[np.ndarray] = None