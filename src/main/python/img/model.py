from typing import Union, Tuple

import numpy as np
from PIL import Image
from PyQt5.QtGui import QImage
from dataclasses import dataclass


@dataclass
class NdImageData:
    ndimg: np.ndarray
    color_mode: str


Img = Union[Image.Image, np.ndarray, QImage]

ituple = Tuple[int, int]
ituples = Tuple[ituple, ...]
ftuple = Tuple[float, float]