from typing import Callable

from PyQt5.QtCore import QObject, QPoint, QTimeLine
from dataclasses import dataclass, InitVar, field


@dataclass
class PanTimeLineData:
    pan: QPoint
    prev_time_line_value: float = 0


@dataclass
class PanTimeLine(QTimeLine):
    value_changed_callback: Callable[[float, PanTimeLineData], None]
    pan_time_line_data: PanTimeLineData = field(init=False)
    pan: InitVar[QPoint]
    parent: InitVar[QObject] = field(default=None)
    duration: InitVar[int] = 400
    update_interval: InitVar[int] = 15

    def __post_init__(self, pan: QPoint, parent: QObject, duration: int, update_interval: int):
        super().__init__(duration, parent)
        self.pan_time_line_data = PanTimeLineData(pan=pan)
        timeline = self
        timeline.setUpdateInterval(update_interval)
        timeline.valueChanged.connect(self.__on_value_changed)

    def __on_value_changed(self, time_line_value: float) -> None:
        self.value_changed_callback(time_line_value, self.pan_time_line_data)
