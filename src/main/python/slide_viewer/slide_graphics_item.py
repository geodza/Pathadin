import os
from bisect import bisect_left
import typing
from concurrent.futures import ThreadPoolExecutor
import openslide
from PyQt5 import QtGui, QtCore
from PyQt5.QtCore import QRectF, QSizeF, QPointF, QRect, Qt, QMutex, QMutexLocker, QPoint
from PyQt5.QtGui import *
from PyQt5.QtWidgets import QGraphicsItem, QWidget, QStyleOptionGraphicsItem

from slide_viewer.common import pilimage_to_pixmap
from slide_viewer.config import debug, cell_size
from slide_viewer.slide_helper import SlideHelper

cache_mutex = QMutex()


def load_tile(slide_path, level0_pos, level, size):
    with openslide.open_slide(slide_path) as slide:
        tile_pilimage = slide.read_region((int(level0_pos[0]), int(level0_pos[1])), level,
                                          (int(size[0]), int(size[1])))
        return tile_pilimage


class SlideGraphicsItem(QGraphicsItem):
    def __init__(self, slide_path: str):
        super().__init__()
        self.slide_helper = SlideHelper(slide_path)
        self.level0_size = self.slide_helper.level_dimensions[0]
        self.level0_qrectf = QRectF(QRect(0, 0, self.level0_size[0], self.level0_size[1]))
        self.cell_size = cell_size

        self.debug = debug

        # self.setFlag(QGraphicsItem.ItemClipsToShape, True)
        # self.setFlag(QGraphicsItem.ItemClipsChildrenToShape, True)
        self.setFlag(QGraphicsItem.ItemUsesExtendedStyleOption, True)
        max_workers = os.cpu_count()
        max_workers = max_workers - 1 if max_workers > 1 else max_workers
        self.thread_pool = ThreadPoolExecutor(max_workers=max_workers)
        self.ongoing_cell_loading = {}
        self.paint_called_count = 0

    def boundingRect(self) -> QtCore.QRectF:
        return self.level0_qrectf

    def paint(self, painter: QtGui.QPainter, option: QStyleOptionGraphicsItem,
              widget: typing.Optional[QWidget] = ...) -> None:
        painter.save()
        self.paint_called_count += 1
        # print("self.paint_called_count", self.paint_called_count)
        # painter.setClipRect(option.exposedRect)

        current_scale = painter.transform().m11()
        current_downsample = 1 / current_scale
        best_level_index = bisect_left(self.slide_helper.level_downsamples, current_downsample)
        # best_level_index=best_level_index-1 if best_level_index==len(self.slide_helper.level_downsamples) else best_level_index
        best_level_index = 0 if best_level_index - 1 == -1 else best_level_index - 1
        best_downsample = self.slide_helper.level_downsamples[best_level_index]

        # level = self.slide_helper.get_best_level_for_downsample(1 / current_scale)
        level = best_level_index
        # level_downsample = self.slide_helper.get_downsample_for_level(level)
        level_downsample = best_downsample
        painter.scale(level_downsample, level_downsample)

        # print("current_scale: {}; downsample: {}; best_downsample: {}; 1/downsample: {}".format(current_scale,
        #                                                                                         int(level_downsample),
        #                                                                                         int(best_downsample),
        #                                                                                         1 / level_downsample))

        scene_to_level = QTransform.fromScale(1 / level_downsample, 1 / level_downsample)
        level_to_scene = QTransform.fromScale(level_downsample, level_downsample)
        level_to_cell = QTransform.fromScale(1 / self.cell_size, 1 / self.cell_size)
        cell_to_level = QTransform.fromScale(self.cell_size, self.cell_size)

        exposed_scene_rect = option.exposedRect
        exposed_level_rect = scene_to_level.mapRect(exposed_scene_rect)
        exposed_cell_rect = level_to_cell.mapRect(exposed_level_rect).toAlignedRect()
        for cell_row in range(exposed_cell_rect.top(), exposed_cell_rect.bottom() + 1):
            for cell_column in range(exposed_cell_rect.left(), exposed_cell_rect.right() + 1):
                cache_key = self.build_cell_cache_key(level, cell_row, cell_column)
                cell_rect = QRect(cell_column, cell_row, 1, 1)
                cell_level_rect = cell_to_level.mapRect(cell_rect)
                cell_scene_rect = level_to_scene.mapRect(cell_level_rect)
                cell_exposed_level_rect = exposed_level_rect.intersected(QRectF(cell_level_rect))
                cell_pixmap_exposed_level_rect = cell_exposed_level_rect.translated(-cell_level_rect.topLeft())

                cache_mutex_locker = QMutexLocker(cache_mutex)
                cell_pixmap = QPixmapCache.find(cache_key)
                if cell_pixmap:
                    cache_mutex_locker.unlock()
                    painter.drawPixmap(cell_exposed_level_rect, cell_pixmap, cell_pixmap_exposed_level_rect)
                else:
                    if not self.ongoing_cell_loading.get(cache_key, False):
                        self.ongoing_cell_loading[cache_key] = True
                        cache_mutex_locker.unlock()
                        cell_pilimage_future = self.thread_pool.submit(load_tile, self.slide_helper.slide_path,
                                                                       (cell_scene_rect.left(), cell_scene_rect.top()),
                                                                       level, (self.cell_size, self.cell_size))
                        # we must update whole cell_scene_rect and not just cell_exposed_scene_rect because by the
                        # time the tile loads, our view can be already in another place (if we scroll a bit) and then
                        # exposedRect will differ from old exposedRect
                        done_callback = self.build_done_callback_closure(cache_key, QRectF(cell_scene_rect))
                        cell_pilimage_future.add_done_callback(done_callback)
                    else:
                        cache_mutex_locker.unlock()

                    for higher_level in range(level + 1, self.slide_helper.get_max_level() + 1):
                        higher_level_downsample = self.slide_helper.get_downsample_for_level(higher_level)
                        # downsample may be not an integer (for example 4.0001) but current logic requires integer.
                        # Due to conversion inaccuracy may be a couple of pixels but it's not so important
                        # because it's only temporal painting
                        relative_downsample = 1 / int(round(higher_level_downsample / level_downsample))
                        level_to_higherlevel = QTransform.fromScale(relative_downsample, relative_downsample)
                        cell_higherlevel_rect = level_to_higherlevel.mapRect(cell_level_rect)
                        higherlevel_cell_rect = level_to_cell.mapRect(QRectF(cell_higherlevel_rect)).toAlignedRect()
                        higherlevel_cache_key = self.build_cell_cache_key(higher_level,
                                                                          higherlevel_cell_rect.top(),
                                                                          higherlevel_cell_rect.left())
                        cache_mutex_locker = QMutexLocker(cache_mutex)
                        higherlevel_cell_pixmap = QPixmapCache.find(higherlevel_cache_key)
                        cache_mutex_locker.unlock()
                        if higherlevel_cell_pixmap:
                            higherlevel_cell_higherlevel_rect = cell_to_level.mapRect(higherlevel_cell_rect)
                            cell_higherlevel_part_rect = cell_higherlevel_rect.translated(
                                -higherlevel_cell_higherlevel_rect.topLeft())
                            painter.drawPixmap(QRectF(cell_level_rect), higherlevel_cell_pixmap,
                                               QRectF(cell_higherlevel_part_rect))
                            break
                self.paint_debug_temp_rects(painter, cell_level_rect, cache_key)

        painter.restore()

    def build_cell_cache_key(self, level, cell_row, cell_column):
        return "{}_({},{})".format(level, cell_row, cell_column)

    def build_done_callback_closure(self, cache_key, scene_rect_to_update):
        def done_callback(cell_pilimage_future):
            cell_pixmap = pilimage_to_pixmap(cell_pilimage_future.result())
            cache_mutex_locker = QMutexLocker(cache_mutex)
            QPixmapCache.insert(cache_key, cell_pixmap)
            self.ongoing_cell_loading[cache_key] = False
            cache_mutex_locker.unlock()
            self.scene().update(scene_rect_to_update.translated(self.pos()))

        return done_callback

    def paint_debug_temp_rects(self, painter: QtGui.QPainter, cell_level_rect, cell_cache_key):
        if self.debug:
            painter.save()
            painter.setPen(QPen(QBrush(Qt.black), 10))
            painter.setBrush(QBrush(QColor.fromRgb(0, 0, 255, 70)))
            painter.setFont(QFont(painter.fontInfo().family(), 30, QFont.Bold))
            painter.drawRect(cell_level_rect)
            painter.drawText(cell_level_rect, Qt.AlignCenter, cell_cache_key)
            painter.restore()
