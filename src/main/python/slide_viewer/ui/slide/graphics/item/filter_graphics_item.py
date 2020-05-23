import typing
from bisect import bisect_left

from PyQt5 import QtGui, QtCore
from PyQt5.QtCore import Qt, pyqtSignal, QRectF
from PyQt5.QtGui import *
from PyQt5.QtWidgets import QGraphicsItem, QWidget, QStyleOptionGraphicsItem, QGraphicsObject
from dataclasses import dataclass

from slide_viewer.common.slide_helper import SlideHelper
from slide_viewer.ui.slide.graphics.item.annotation.annotation_graphics_item import AnnotationGraphicsItem
from slide_viewer.ui.slide.widget.interface.annotation_pixmap_provider import AnnotationItemPixmapProvider


@dataclass
class FilterGraphicsItem(QGraphicsObject):
    pixmap_provider: AnnotationItemPixmapProvider
    slide_helper: SlideHelper

    def __post_init__(self):
        QGraphicsObject.__init__(self)
        self.setFlag(QGraphicsItem.ItemUsesExtendedStyleOption)

    def boundingRect(self) -> QtCore.QRectF:
        # return self.bounding_rect
        return self.scene().sceneRect()

    def paint(self, painter: QtGui.QPainter, option: QStyleOptionGraphicsItem,
              widget: typing.Optional[QWidget] = None) -> None:
        exposed_scene_rect = option.exposedRect
        current_scale = painter.transform().m11()
        painter.save()
        for item in self.exposed_annotation_items(exposed_scene_rect):
            # level_pixmap = self.pixmap_provider.get_pixmap(item.id, lambda: self.update())
            level_pixmap = self.pixmap_provider.get_pixmap(item.id, self.update)
            if level_pixmap:
                level, pixmap = level_pixmap
                # level_to_scene = QTransform().fromScale(current_scale, current_scale)

                current_scale = painter.transform().m11()
                painter.save()
                current_downsample = 1 / current_scale
                best_level_index = bisect_left(self.slide_helper.level_downsamples, current_downsample)
                best_level_index = 0 if best_level_index - 1 == -1 else best_level_index - 1
                best_downsample = self.slide_helper.level_downsamples[best_level_index]

                level = best_level_index
                level_downsample = best_downsample

                level_downsample = self.slide_helper.level_downsamples[level]
                painter.scale(level_downsample, level_downsample)
                # painter.scale(current_downsample, current_downsample)

                scene_to_level = QTransform.fromScale(1 / level_downsample, 1 / level_downsample)
                item_level_rect = scene_to_level.mapRect(item.boundingRect().translated(item.pos()).toRect())
                painter.drawPixmap(item_level_rect, pixmap, pixmap.rect())
                painter.restore()
            else:
                # f = painter.font()
                # f.setPointSize(50)
                # painter.setFont(f)
                # painter.drawText(item.boundingRect().translated(item.pos()), "In progress...")
                pass
        painter.restore()

    def exposed_annotation_items(self, rect: QRectF):
        items = self.scene().items(rect, Qt.IntersectsItemBoundingRect)
        return [i for i in items if isinstance(i, AnnotationGraphicsItem)]
