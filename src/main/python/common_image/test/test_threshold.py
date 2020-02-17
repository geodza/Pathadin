import numpy as np

from common_image.core.threshold import ndimg_to_thresholded_ndimg
from common_image.model.ndimagedata import NdImageData

if __name__ == '__main__':
    a = np.arange(255 * 2 * 4 * 3).reshape((255, 2, 4, 3))
    np.transpose(a, axes=(0, 2, 3, 1))[..., 0, :] = [20, 60]
    print(a[:, 0, :, :])

    ndimg = NdImageData(np.array([[
        [160, 40, 50],
        [20, 40, 50],
        [50, 40, 50]
    ]
    ], dtype=np.uint8), 'HSV')
    # j=np.take(ndimg.ndimg, [[0,2],[0,2],])
    j = ndimg.ndimg[[0], [1], :]
    i = ndimg.ndimg[:, :, [1]]
    thres = ((150, 30, 40), (30, 50, 60))
    res = ndimg_to_thresholded_ndimg(ndimg, thres)
    a = np.array((50, 100))
    b = np.array(((10, 20, 30), (40, 50, 10)))
    c = b[0] > b[1]
    bc = np.copy(b)
    bc[0, c] = 0
    bc[1, c] = 255
    print(a, b, c)
