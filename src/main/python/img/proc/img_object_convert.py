import io

import numpy as np
from PIL import Image
from PIL.ImageQt import ImageQt
from PyQt5.QtCore import QBuffer
from PyQt5.QtGui import QImage, QPixmap


# https://stackoverflow.com/questions/47289884/how-to-convert-qimageqpixmap-to-pil-image-in-python-3?noredirect=1&lq=1

# be careful, use QPixmap only in main GUI thread

# def expose_ndarray_to_qimage(ndarray: np.array):
# img = QImage(ndarray, ndarray.shape[1], ndarray.shape[0], QImage.Format_Indexed8)
# return img


def qimage_to_pillowimage(qimg: QImage) -> Image.Image:
    buffer = QBuffer()
    buffer.open(QBuffer.ReadWrite)
    qimg.save(buffer, "PNG")
    pillowimage = Image.open(io.BytesIO(buffer.data()))
    buffer.close()
    return pillowimage


def expose_pilimage_buffer_to_ndarray(pilimg: Image.Image) -> np.ndarray:
    return np.array(pilimg)
    b = pilimg.tobytes()
    # TODO is np.array(img) or np.array(img.getdata()) better than tobytes()?
    # For raw types (like bmp, png) img.getdata() will return really internal buffer without any additional memory allocation? and tobytes() will allocate?
    arr = np.frombuffer(b, dtype=np.uint8)
    r, c, ch = pilimg.height, pilimg.width, len(pilimg.getbands())
    arr = arr.reshape((r, c, ch))
    # setattr(pilimg, 'arr', arr)
    return arr


def expose_ndarray_buffer_to_pillowimage(arr: np.ndarray, mode: str) -> Image.Image:
    h, w, *a = arr.shape
    pilimg = Image.frombuffer(mode, (w, h), arr, 'raw', mode, 0, 1)
    # setattr(pilimg, 'arr', arr)
    return pilimg


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