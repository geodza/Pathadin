from typing import Callable

from PyQt5.QtCore import QTimeLine, QObject
from dataclasses import dataclass, InitVar, field


@dataclass
class ScaleTimeLineData:
    scale_factor: float
    prev_time_line_value: float = 0


@dataclass
class ScaleTimeLine(QTimeLine):
    value_changed_callback: Callable[[float, ScaleTimeLineData], None]
    scale_time_line_data: ScaleTimeLineData = field(init=False)
    scale_factor: InitVar[float]
    parent: InitVar[QObject] = field(default=None)
    duration: InitVar[int] = 250
    update_interval: InitVar[int] = 15

    def __post_init__(self, scale_factor: float, parent: QObject, duration: int, update_interval: int):
        super().__init__(duration, parent)
        self.scale_time_line_data = ScaleTimeLineData(scale_factor=scale_factor)
        timeline = self
        timeline.setUpdateInterval(update_interval)
        timeline.valueChanged.connect(self.on_value_changed)

    def on_value_changed(self, time_line_value: float) -> None:
        self.value_changed_callback(time_line_value, self.scale_time_line_data)
