import io

import numpy as np
from PIL import Image
from PIL.ImageQt import ImageQt
from PyQt5.QtCore import QBuffer
from PyQt5.QtGui import QImage, QBitmap, QPixmap

from common_image.model.ndimg import Ndimg
from common_qt.util.qobjects_convert_util import ituple_to_qsize


def ndimg_to_qimg(img: Ndimg) -> QImage:
    if img.color_mode == 'RGBA':
        format = QImage.Format_RGBA8888
    elif img.color_mode == 'RGB':
        format = QImage.Format_RGB888
    elif img.color_mode == 'L':
        format = QImage.Format_Grayscale8
    else:
        raise ValueError(f"Unsupported img color mode: {img.color_mode}")
    ndimg = img.ndarray
    h, w, *ch = ndimg.shape
    ch = ch[0] if ch else 1
    img = QImage(ndimg, w, h, w * ch, format)
    img.__dict__['ndimg'] = ndimg
    return img


def ndimg_to_bitmap(bool_mask_ndimg: np.ndarray) -> QBitmap:
    mask_bits = np.packbits(bool_mask_ndimg, axis=-1)
    bitmap_size = ituple_to_qsize(bool_mask_ndimg.shape[::-1])
    mask_bits_bytes = mask_bits.tobytes()
    bitmap = QBitmap.fromData(bitmap_size, mask_bits_bytes, format=QImage.Format_Mono)
    # cache_['123'] = mask_bits_bytes
    # bitmap.__dict__['mask_bits'] = mask_bits_bytes
    return bitmap


def qimage_to_pillowimage(qimg: QImage) -> Image.Image:
    buffer = QBuffer()
    buffer.open(QBuffer.ReadWrite)
    qimg.save(buffer, "PNG")
    pillowimage = Image.open(io.BytesIO(buffer.data()))
    buffer.close()
    return pillowimage


def expose_qimage_buffer_to_pillowimage(qimg: QImage) -> Image.Image:
    buffer = qimg.constBits()
    buffer.setsize(qimg.byteCount())
    pillowimage = Image.frombuffer("RGBA", (qimg.width(), qimg.height()), buffer, "raw", "RGBA", 0, 1)
    return pillowimage


def expose_qimage_buffer_to_ndarray(qimg: QImage) -> np.ndarray:
    # qimg = qimg.rgbSwapped()
    w, h = qimg.width(), qimg.height()
    ch = qimg.byteCount() // (w * h)
    buffer = qimg.constBits()
    buffer.setsize(w * h * ch)
    # dt = np.dtype([('R', 'u1'), ('G', 'u1'), ('B', 'u1'), ('A', 'u1')])
    # dt = np.dtype((np.uint8, (h, w, ch)))
    # dt = np.dtype(((np.uint32, (np.uint8, 4)), (h, w)))
    # dt = np.dtype(((np.uint32, (np.uint8, 4)), (h, w)))
    # arr = np.frombuffer(buffer, dt).reshape((h, w, ch))
    arr = np.frombuffer(buffer, f'u{ch}')
    arr = arr.reshape((h, w))
    # arr = np.asarray(arr, order='C')
    arr = arr.view(np.uint8)
    arr = arr.reshape((h, w, ch))
    return arr


def pilimage_to_pixmap(pilimg) -> QPixmap:
    qim = ImageQt(pilimg)
    pix = QPixmap.fromImage(qim)
    return pix


def pilimage_to_qimage(pilimg) -> QImage:
    qim = ImageQt(pilimg)
    return qim