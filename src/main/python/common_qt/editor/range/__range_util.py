from common_image.model.color_mode import ColorMode


def default_range(color_mode):
    d = {
        ColorMode.HSV: ((0, 0, 0), (255, 255, 255)),
        ColorMode.L: (0, 255)
    }
    return d[color_mode]


def is_valid_range(range_, color_mode):
    d = {
        ColorMode.HSV: is_valid_hsv_range,
        ColorMode.L: is_valid_gray_range,
    }
    return d[color_mode](range_)


def is_valid_hsv_range(range_):
    try:
        return len(range_) == 2 and len(range_[0]) == 3 and len(range_[1]) == 3
    except:
        return False


def is_valid_gray_range(range_):
    try:
        return len(range_) == 2 and isinstance(range_[0], int) and isinstance(range_[1], int)
    except:
        return False