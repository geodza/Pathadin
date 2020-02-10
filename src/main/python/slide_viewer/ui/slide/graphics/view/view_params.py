import typing

from PyQt5.QtCore import QPointF, QPoint
from dataclasses import dataclass


@dataclass
class ViewParams:
    mouse_scene_pos: typing.Optional[QPointF] = None
    mouse_pos: typing.Optional[QPoint] = None
    mouse_move_between_press_and_release: bool = False