from typing import Union

import numpy as np
from PIL import Image
from PyQt5.QtGui import QImage

Img = Union[Image.Image, np.ndarray, QImage]