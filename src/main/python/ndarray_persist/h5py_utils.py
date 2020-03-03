import h5py
import numpy as np
from h5py import Dataset


def update_dataset_image_attrs(dataset: Dataset) -> None:
    if len(dataset.shape) == 2:
        attrs = {"CLASS": np.string_('IMAGE'),
                 "IMAGE_VERSION": np.string_("1.2"),
                 "IMAGE_MINMAXRANGE": np.asarray([0, 255], dtype=np.uint8),
                 "IMAGE_SUBCLASS": np.string_('IMAGE_GRAYSCALE')}
    else:
        attrs = {"CLASS": np.string_('IMAGE'),
                 "IMAGE_VERSION": np.string_("1.2"),
                 "IMAGE_MINMAXRANGE": np.asarray([0, 255], dtype=np.uint8),
                 "IMAGE_SUBCLASS": np.string_('IMAGE_TRUECOLOR'),
                 "INTERLACE_MODE": np.string_('INTERLACE_PIXEL')}
    dataset.attrs.update(attrs)


if __name__ == '__main__':
    with h5py.File('gray_img.hdf5', 'w') as f:
        img = np.random.rand(100, 100) * 255
        img = img.astype(np.uint8)
        dataset = f.create_dataset('img1', data=img)
        update_dataset_image_attrs(dataset)
