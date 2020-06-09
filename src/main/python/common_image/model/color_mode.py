from enum import unique, Enum


@unique
class ColorMode(str, Enum):
    L = 'L'
    HSV = 'HSV'
    # RGB = 3
