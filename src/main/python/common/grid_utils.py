from itertools import product
from math import ceil
from typing import Tuple


# mapRect???

def grid_pos_to_source_pos(grid_pos: Tuple[int, int], grid_length: int) -> Tuple[int, int]:
    # (row,col)->(x,y)
    x = grid_pos[1] * grid_length
    y = grid_pos[0] * grid_length
    return x, y


def grid_flat_pos_to_grid_pos(grid_flat_pos: int, grid_nrows: int) -> Tuple[int, int]:
    row = grid_flat_pos // grid_nrows
    # col = grid_flat_pos - row * grid_nrows
    col = grid_flat_pos % grid_nrows
    return (row, col)


def grid_flat_pos_range(source_size: Tuple[int, int], grid_length: int):
    # row,col
    sw, sh = source_size
    gw, gh = grid_length, grid_length
    cols = ceil(sw / gw)
    rows = ceil(sh / gh)
    return range(rows * cols)


def pos_to_rect_coords(pos: Tuple[int, int], grid_length: int) -> Tuple[int, int, int, int]:
    return pos[0], pos[1], pos[0] + grid_length, pos[1] + grid_length


def grid_pos_range(source_size: Tuple[int, int], grid_length: int):
    # row,col
    sw, sh = source_size
    gw, gh = grid_length, grid_length
    cols = ceil(sw / gw)
    rows = ceil(sh / gh)
    return product(range(rows), range(cols))


# def pos_range(source_size: Tuple[int, int], grid_length: int, x_offset: int = 0, y_offset: int = 0):
#     # x,y
#     sw, sh = source_size
#     gw, gh = grid_length, grid_length
#     cols = ceil(sw / gw)
#     rows = ceil(sh / gh)
#     return ((x_offset + col * grid_length, y_offset + row * grid_length) for row in range(rows) for col in range(cols))

def pos_range(source_size: Tuple[int, int], x_stride: int, y_stride: int, x_offset: int = 0, y_offset: int = 0):
    # x,y
    sw, sh = source_size
    if x_stride <= 0:
        x_stride = source_size[0]
    elif x_stride <= 1:
        x_stride = source_size[0] * x_stride
    if y_stride <= 0:
        y_stride = source_size[1]
    elif y_stride <= 1:
        y_stride = source_size[1] * y_stride

    cols = ceil((sw - x_offset) / x_stride)
    rows = ceil((sh - y_offset) / y_stride)
    return ((int(x_offset + col * x_stride), int(y_offset + row * y_stride)) for row in range(rows) for col in range(cols))


if __name__ == '__main__':
    print(list(pos_range((100, 500), -1, 10)))
