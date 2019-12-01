import cv2
import numpy as np
from PIL import Image

from slide_viewer.ui.common.img.img_object_convert import expose_pilimage_buffer_to_ndarray, \
    expose_ndarray_buffer_to_pillowimage
# def build_opencvcolor_to_pillowmode_dict():
#     opencvcolor_to_pillowmode_dict = {}
#     color_convertion_names = [c for c in dir(cv2) if c.startswith("COLOR")]
#     for ccn in color_convertion_names:
#         if ccn.endswith("2GRAY"):
#             mode = "L"
#         elif ccn.endswith("2RGB"):
#             mode = "RGB"
#         elif ccn.endswith("2RGBA"):
#             mode = "RGBA"
#         else:
#             continue
#         color_convertion_value = getattr(cv2, ccn)
#         opencvcolor_to_pillowmode_dict[color_convertion_value] = mode
#     return opencvcolor_to_pillowmode_dict
#
#
# opencvcolor_to_pillowmode_dict = build_opencvcolor_to_pillowmode_dict()
#
# def opencvcolorconvertion_to_pillowmode(colorconvertion: int):
#     return opencvcolor_to_pillowmode_dict[colorconvertion]
from slide_viewer.ui.model.filter.base_filter import FilterResults


# NOTE on colorspace in common
# https://imagemagick.org/script/formats.php#colorspace
# A majority of the image formats assume an sRGB colorspace (e.g. JPEG, PNG, etc.). A few support only linear RGB (e.g. EXR, DPX, CIN, HDR) or only linear GRAY (e.g. PGM). A few formats support CMYK. Then there is the occasional format that also supports LAB (that is CieLAB) (e.g. TIFF, PSD, JPG, JP2).
# NOTE on openslide`s bit-depth and colorspace of output image
# from openslide sources:
#
# ImageSlide.read_region: tile = Image.new("RGBA", size, (0,) * 4) -- RGBA (4x8-bit pixels, true color with transparency mask)
#
# OpenSlide.read_region:
#   buf = (w * h * c_uint32)() -- c_uint32 for RGBA means uint_8 for each channel. So format is the same as above
#   ...
#   return PIL.Image.frombuffer('RGBA', size, buf, 'raw', 'RGBA', 0, 1)
#
# So if we use read_region, then we always have output image of this mode: RGBA (4x8-bit pixels, true color with transparency mask)


def get_cvtcolor_values(mode_from: str, mode_to: str):
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


def convert_pilimage(pilimg: Image, required_mode: str) -> Image.Image:
    if pilimg.mode == required_mode:
        return pilimg
    cvtcolor_values = get_cvtcolor_values(pilimg.mode, required_mode)
    # cv2 cant convert to CMYK and pillow cant convert to LAB, so we combine their convert possibilities
    if None in cvtcolor_values or (pilimg.mode == 'HSV'):
        pilimg = pilimg.convert(required_mode)
        return pilimg
    else:
        arr = expose_pilimage_buffer_to_ndarray(pilimg)
        for cvtcolor_value in cvtcolor_values:
            arr = cv2.cvtColor(arr, cvtcolor_value)
        pilimg = expose_ndarray_buffer_to_pillowimage(arr, required_mode)
        return pilimg


def convert_ndimg(ndimg: np.ndarray, current_mode: str, required_mode: str) -> np.ndarray:
    if current_mode == required_mode:
        return ndimg
    cvtcolor_values = get_cvtcolor_values(current_mode, required_mode)
    # cv2 cant convert to CMYK and pillow cant convert to LAB, so we combine their convert possibilities
    # if None in cvtcolor_values or (current_mode == 'HSV'):
    #     pilimg = pilimg.convert(required_mode)
    #     return pilimg
    # else:
    for cvtcolor_value in cvtcolor_values:
        ndimg = cv2.cvtColor(ndimg, cvtcolor_value)
    return ndimg


def convert_filter_results(fr: FilterResults, required_mode: str) -> FilterResults:
    if isinstance(fr.img, Image.Image):
        fr.color_mode = required_mode
        fr.img = convert_pilimage(fr.img, required_mode)
        return fr
    elif isinstance(fr.img, np.ndarray):
        fr.img = convert_ndimg(fr.img, fr.color_mode, required_mode)
        fr.color_mode = required_mode
        return fr
    else:
        raise ValueError(f"Unsupported img type for convert: {fr.img}")
