from typing import List

import cv2
import numpy as np

from common_image.model.ndimg import Ndimg


def convert_ndimg(ndimg: Ndimg, required_mode: str) -> Ndimg:
    return Ndimg(convert_ndarray(ndimg.ndarray, ndimg.color_mode, required_mode), required_mode, ndimg.bool_mask_ndarray)


def convert_ndarray(ndarray: np.ndarray, current_mode: str, required_mode: str) -> np.ndarray:
    if current_mode == required_mode:
        return ndarray
    cvtcolor_values = get_cvtcolor_values(current_mode, required_mode)
    for cvtcolor_value in cvtcolor_values:
        if cvtcolor_value is not None:
            ndarray = cv2.cvtColor(ndarray, cvtcolor_value)
            ndarray = np.atleast_3d(ndarray)
    return ndarray


def get_cvtcolor_values(mode_from: str, mode_to: str) -> List[int]:
    if mode_from == "RGBA":
        return [cv2.COLOR_RGBA2RGB, *get_cvtcolor_values("RGB", mode_to)]
    elif mode_to == "RGBA":
        return [*get_cvtcolor_values(mode_from, "RGB"), cv2.COLOR_RGB2RGBA]
    pilmode_to_cvtcolor = {
        "L": "GRAY",
    }
    cvtcolor_from = pilmode_to_cvtcolor.get(mode_from, mode_from)
    cvtcolor_to = pilmode_to_cvtcolor.get(mode_to, mode_to)
    cvtcolor = f"COLOR_{cvtcolor_from}2{cvtcolor_to}"
    cvtcolor_value = getattr(cv2, cvtcolor, None)
    return [cvtcolor_value]
