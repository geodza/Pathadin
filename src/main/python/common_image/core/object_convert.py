import numpy as np
from PIL import Image

# def expose_ndarray_to_qimage(ndarray: np.array):
# img = QImage(ndarray, ndarray.shape[1], ndarray.shape[0], QImage.Format_Indexed8)
# return img
from common.timeit_utils import timing
from common_image.model.ndimg import Ndimg


# https://stackoverflow.com/questions/47289884/how-to-convert-qimageqpixmap-to-pil-image-in-python-3?noredirect=1&lq=1
# be careful, use QPixmap only in main GUI thread


def expose_ndarray_buffer_to_pilimg(ndarray: np.ndarray, mode: str) -> Image.Image:
    h, w, *a = ndarray.shape
    pilimg = Image.frombuffer(mode, (w, h), ndarray, 'raw', mode, 0, 1)
    # setattr(pilimg, 'arr', arr)
    return pilimg


def expose_ndimg_buffer_to_pilimg(ndimg: Ndimg) -> Image.Image:
    return expose_ndarray_buffer_to_pilimg(ndimg.ndarray, ndimg.color_mode)


def pilimg_to_ndarray(pilimg: Image.Image) -> np.ndarray:
    ndarray = np.array(pilimg)
    return ndarray


@timing
def pilimg_to_ndimg(pilimg: Image.Image) -> Ndimg:
    ndarray = np.array(pilimg)
    return Ndimg(ndarray, pilimg.mode)
