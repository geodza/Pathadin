import typing

from PyQt5.QtCore import pyqtSignal, QRectF
from PyQt5.QtGui import QTransform
from PyQt5.QtWidgets import QGraphicsView, QWidget


class GraphicsViewTransformNotifier(QGraphicsView):
    transformChanged = pyqtSignal(QTransform, bool)
    viewUpdated = pyqtSignal()
    viewSceneRectUpdated = pyqtSignal(QRectF)
    viewSceneRectsUpdated = pyqtSignal(list)

    def __init__(self, parent: typing.Optional[QWidget] = None) -> None:
        super().__init__(parent)

    def emit_transform_changed(self):
        self.transformChanged.emit(self.transform(), False)

    def setTransform(self, matrix: QTransform, combine: bool = False) -> None:
        # self.resetTransform()
        super().setTransform(matrix, combine)
        self.emit_transform_changed()

    def resetTransform(self) -> None:
        super().resetTransform()
        self.horizontalScrollBar().setValue(0)
        self.verticalScrollBar().setValue(0)
        self.emit_transform_changed()

    def shear(self, sh: float, sv: float) -> None:
        super().shear(sh, sv)
        self.emit_transform_changed()

    def scale(self, sx: float, sy: float) -> None:
        super().scale(sx, sy)
        self.emit_transform_changed()

    def rotate(self, angle: float) -> None:
        super().rotate(angle)
        self.emit_transform_changed()

    def translate(self, dx: float, dy: float) -> None:
        super().translate(dx, dy)
        self.emit_transform_changed()

    def update(self) -> None:
        super().update()
        self.viewUpdated.emit()

    def updateSceneRect(self, rect: QRectF) -> None:
        super().updateSceneRect(rect)
        self.viewSceneRectUpdated.emit(rect)

    def updateScene(self, rects: typing.Iterable[QRectF]) -> None:
        super().updateScene(rects)
        self.viewSceneRectsUpdated.emit(list(rects))

    # Forbid methods that use scrollbars
    scrollContentsBy = None
    fitInView = None
    ensureVisible = None
    centerOn = None
