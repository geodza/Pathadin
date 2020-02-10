import numpy as np
from PIL import Image
from PyQt5.QtGui import QImage, QBitmap

from img.ndimagedata import NdImageData
from slide_viewer.common_qt.qobjects_convert_util import ituple_to_qsize


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


def ndimg_to_bitmap(bool_mask_ndimg: np.ndarray) -> QBitmap:
    mask_bits = np.packbits(bool_mask_ndimg,axis=-1)
    bitmap_size = ituple_to_qsize(bool_mask_ndimg.shape[::-1])
    mask_bits_bytes = mask_bits.tobytes()
    bitmap = QBitmap.fromData(bitmap_size, mask_bits_bytes, format=QImage.Format_Mono)
    # cache_['123'] = mask_bits_bytes
    # bitmap.__dict__['mask_bits'] = mask_bits_bytes
    return bitmap