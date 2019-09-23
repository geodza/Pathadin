from PyQt5.QtCore import QTimeLine, QObject, pyqtSignal


class ScaleTimeLineData:
    def __init__(self, scale_factor: float):
        self.scale_factor: float = scale_factor
        self.prev_time_line_value: float = 0


class SlideViewerScaleTimeLine(QTimeLine):

    def __init__(self, parent: QObject, scale_factor: float, value_changed_callback) -> None:
        super().__init__(250, parent)
        self.value_changed_callback = value_changed_callback
        timeline = self
        timeline.setUpdateInterval(15)
        timeline.setProperty("scale_time_line_data", ScaleTimeLineData(scale_factor))
        timeline.valueChanged.connect(self.on_value_changed)

    def on_value_changed(self, time_line_value: float):
        self.value_changed_callback(time_line_value, self.property("scale_time_line_data"))
