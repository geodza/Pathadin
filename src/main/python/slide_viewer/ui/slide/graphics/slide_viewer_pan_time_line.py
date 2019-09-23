from PyQt5.QtCore import QTimeLine, QObject, pyqtSignal, QPoint


class PanTimeLineData:
    def __init__(self, pan: QPoint):
        self.pan: QPoint = pan
        self.prev_time_line_value: float = 0


class SlideViewerPanTimeLine(QTimeLine):

    def __init__(self, parent: QObject, pan: QPoint, value_changed_callback) -> None:
        super().__init__(400, parent)
        self.value_changed_callback = value_changed_callback
        timeline = self
        timeline.setUpdateInterval(15)
        timeline.setProperty("pan_time_line_data", PanTimeLineData(pan))
        timeline.valueChanged.connect(self.on_value_changed)

    def on_value_changed(self, time_line_value: float):
        self.value_changed_callback(time_line_value, self.property("pan_time_line_data"))
