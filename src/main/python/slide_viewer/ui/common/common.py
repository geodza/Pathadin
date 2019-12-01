import inspect

import numpy as np
from PIL import Image
from PyQt5.QtCore import QMimeData
from dataclasses import fields

if __name__ == '__main__':
    im = Image.open(r'C:\Users\User\GoogleDisk\Pictures\32.png')
    b = im.tobytes()
    im2 = Image.frombuffer("L", (32, 32), b)
    # imarr = np.array(im)
    imarr2 = np.frombuffer(b, dtype=np.uint8)
    imarr2[0] = 0
    # im.show()


def mime_data_is_url(mime_data: QMimeData):
    return mime_data.hasUrls() and len(mime_data.urls()) == 1


def join_odict_values(odict, odict_display_attr_keys):
    display_values = []
    for attr_key in odict_display_attr_keys:
        attr_value = odict.get(attr_key, None)
        # display_value = f"{attr_key}: {attr_value}"
        display_value = f"{attr_value}"
        display_values.append(display_value)
    display_str = "\n".join(display_values)
    return display_str


# https://stackoverflow.com/questions/12627118/get-a-function-arguments-default-value
def get_default_args(func):
    signature = inspect.signature(func)
    return {
        k: v.default
        for k, v in signature.parameters.items()
        if v.default is not inspect.Parameter.empty
    }


def get_default_arg(func, attr: str):
    signature = inspect.signature(func)
    param = signature.parameters[attr]
    return param.default


def field_names(cls):
    return [f.name for f in fields(cls)]
