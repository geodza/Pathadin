from typing import Union

from PyQt5.QtCore import QRect, QRectF, QMargins
from PyQt5.QtGui import QTransform


def print_qrect(qrect: Union[QRect, QRectF]):
    print("(topLeft: ({},{}) bottom_right: ({},{}) width: {} height: {}"
          .format(qrect.left(), qrect.top(), qrect.right(), qrect.bottom(), qrect.width(), qrect.height()))


def print_transform(transform: QTransform):
    print(transform.m11(), transform.m12(), transform.m13(),
          transform.m21(), transform.m22(), transform.m23(),
          transform.m31(), transform.m32(), transform.m33())


def print_margins(margins: QMargins):
    print(margins.top(), margins.left(), margins.bottom(), margins.right())