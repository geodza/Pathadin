from typing import Union

from PIL.ImageQt import ImageQt
from PyQt5.QtCore import QRectF, QSize, QSizeF, QMargins, QRect, QMimeData, QEvent, Qt
from PyQt5.QtGui import QTransform, QPixmap, QKeyEvent

from slide_viewer.config import debug


def print_qrect(qrect: Union[QRect, QRectF]):
    print("(topLeft: ({},{}) bottom_right: ({},{}) width: {} height: {}"
          .format(qrect.left(), qrect.top(), qrect.right(), qrect.bottom(), qrect.width(), qrect.height()))


def print_transform(transform: QTransform):
    print(transform.m11(), transform.m12(), transform.m13(),
          transform.m21(), transform.m22(), transform.m23(),
          transform.m31(), transform.m32(), transform.m33())


def print_margins(margins: QMargins):
    print(margins.top(), margins.left(), margins.bottom(), margins.right())


def pilimage_to_pixmap(pilimage):
    qim = ImageQt(pilimage)
    pix = QPixmap.fromImage(qim)
    return pix


def mime_data_is_url(mime_data: QMimeData):
    return mime_data.hasUrls() and len(mime_data.urls()) == 1


def debug_only(debug_=debug):
    def debug_only_wrap(func):
        def func_wrap(*args, **kwargs):
            if debug_:
                func(*args, **kwargs)

        return func_wrap

    return debug_only_wrap


def is_key_press_event(event: QEvent):
    if event.type() == QEvent.KeyPress:
        key_event: QKeyEvent = event
        if key_event.key() == Qt.Key_Enter or key_event.key() == Qt.Key_Return:
            return True
    return False


def join_odict_values(odict, odict_display_attr_keys):
    display_values = []
    for attr_key in odict_display_attr_keys:
        attr_value = odict.get(attr_key, None)
        # display_value = f"{attr_key}: {attr_value}"
        display_value = f"{attr_value}"
        display_values.append(display_value)
    display_str = "\n".join(display_values)
    return display_str
