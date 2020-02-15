import numpy as np
from PyQt5.QtGui import QBitmap, QImage

from common_qt.qobjects_convert_util import ituple_to_qsize

if __name__ == '__main__':
    # arr1 = np.asarray([0, 0, 0, 0, 0, 0, 1])
    arr1 = np.asarray([[1, 0, 0], [1, 1, 0], [1, 1, 1]])
    mask_bits = np.packbits(arr1)
    bitmap_size = ituple_to_qsize(arr1.shape)
    bitmap = QBitmap.fromData(bitmap_size, mask_bits.tobytes(order='C'), format=QImage.Format_Mono)
    qimg = bitmap.toImage()
    print(mask_bits)
