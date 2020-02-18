from enum import unique, Enum


@unique
class ColorMode(Enum):
    L = 1
    HSV = 2
    RGB = 3
