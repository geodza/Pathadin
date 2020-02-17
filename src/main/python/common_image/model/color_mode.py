from enum import unique, Enum


@unique
class ColorMode(Enum):
    L = 1
    HSV = 2
    RGB = 3


def is_valid_color_mode(mode):
    return mode in ColorMode


def default_color_mode():
    return ColorMode.L
