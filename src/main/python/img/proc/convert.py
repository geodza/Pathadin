import numpy as np
from PIL import Image
from PyQt5.QtGui import QImage

from img.model import NdImageData


def pilimg_to_ndimg(img: Image.Image) -> NdImageData:
    ndimg_ = np.array(img)
    return NdImageData(ndimg_, img.mode)


def ndimg_to_qimg(img: NdImageData) -> QImage:
    if img.color_mode == 'RGBA':
        format = QImage.Format_RGBA8888
    elif img.color_mode == 'RGB':
        format = QImage.Format_RGB888
    elif img.color_mode == 'L':
        format = QImage.Format_Grayscale8
    else:
        raise ValueError(f"Unsupported img color mode: {img.color_mode}")
    ndimg = img.ndimg
    h, w, *ch = ndimg.shape
    ch = ch[0] if ch else 1
    img = QImage(ndimg, w, h, w * ch, format)
    img.__dict__['ndimg'] = ndimg
    return img