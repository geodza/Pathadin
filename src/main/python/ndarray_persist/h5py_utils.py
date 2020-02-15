import numpy as np
from h5py import Dataset


def update_dataset_image_attrs(dataset: Dataset) -> None:
    attrs = {"CLASS": np.string_('IMAGE'),
             "IMAGE_VERSION": np.string_("1.2"),
             "IMAGE_MINMAXRANGE": np.asarray([0, 255], dtype=np.uint8),
             "IMAGE_SUBCLASS": np.string_('IMAGE_TRUECOLOR'),
             "INTERLACE_MODE": np.string_('INTERLACE_PIXEL')}
    dataset.attrs.update(attrs)
