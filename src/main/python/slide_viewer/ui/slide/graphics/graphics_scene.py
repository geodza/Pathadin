import typing
from collections import OrderedDict

from PyQt5.QtCore import QObject, pyqtSignal, QPoint
from PyQt5.QtGui import QColor
from PyQt5.QtWidgets import QGraphicsScene
from dataclasses import dataclass, field

from slide_viewer.common_qt.abcq_meta import ABCQMeta
from slide_viewer.common_qt.qobjects_convert_util import tuples_to_qpoints, tuple_to_qpoint, qpoint_to_tuple
from slide_viewer.common_qt.slot_disconnected import slot_disconnected
from slide_viewer.ui.common.metrics import calc_length, calc_geometry_area
from slide_viewer.ui.odict.deep.base.deepable import deep_get
from slide_viewer.ui.odict.deep.model import AnnotationModel
from slide_viewer.ui.slide.graphics.item.annotation.annotation_figure_graphics_item import \
    AnnotationFigureGraphicsModel
from slide_viewer.ui.slide.graphics.item.annotation.annotation_graphics_item import AnnotationGraphicsItem, \
    AnnotationGraphicsModel
from slide_viewer.ui.slide.graphics.item.annotation.annotation_text_graphics_item import AnnotationTextGraphicsModel
from slide_viewer.ui.slide.graphics.item.annotation.model import AnnotationStats
from slide_viewer.ui.slide.slide_stats_provider import SlideStatsProvider
from slide_viewer.ui.slide.widget.interface.scale_view_provider import ScaleProvider


def build_figure_model(m: AnnotationModel):
    return AnnotationFigureGraphicsModel(m.geometry.annotation_type,
                                         tuples_to_qpoints(m.geometry.points),
                                         QColor(m.figure_graphics_view_config.color))


def build_text_model(m: AnnotationModel):
    text_display_values = [deep_get(m, key) for key in m.text_graphics_view_config.display_attrs]
    # text = '\n'.join(map(str, text_display_values))
    text = '<br/>'.join(map(str, text_display_values))
    # text += '<div style="width:100px">' \
    #         '<div style="background-color:blue; width:40px">40%</div>' \
    #         '<div style="background-color:red; width:60px">60%</div>' \
    #         f'<div><span style="background-color:purple">10%{"."*10}</span></div>' \
    #         f'<div><span style="background-color:orange">20%{"."*20}</span></div>' \
    #         '</div>'
    return AnnotationTextGraphicsModel(text, QColor(m.text_graphics_view_config.background_color))


def build_model(m: AnnotationModel):
    text_model = build_text_model(m)
    figure_model = build_figure_model(m)
    return AnnotationGraphicsModel(tuple_to_qpoint(m.geometry.origin_point), figure_model, text_model,
                                   m.figure_graphics_view_config.hidden, m.text_graphics_view_config.hidden)


@dataclass
class GraphicsScene(QGraphicsScene, SlideStatsProvider, metaclass=ABCQMeta):
    scale_provider: ScaleProvider
    parent_: QObject = field(default=None)
    microns_per_pixel: float = 1
    annotations: typing.Dict[str, AnnotationGraphicsItem] = field(default_factory=OrderedDict)

    annotationModelAdded = pyqtSignal(AnnotationModel)
    annotationModelChanged = pyqtSignal(AnnotationModel)
    annotationModelsRemoved = pyqtSignal(list)
    annotationModelsSelected = pyqtSignal(list)

    def __post_init__(self):
        super().__init__(self.parent_)
        self.selectionChanged.connect(self.__on_selection_changed)
        self.annotationModelChanged.connect(self.__on_update_stats)

    def get_microns_per_pixel(self) -> float:
        return self.microns_per_pixel

    def add_annotation(self, annotation_model: AnnotationModel) -> AnnotationGraphicsItem:
        # annotation_model = annotation_model.copy(deep=True)
        if annotation_model.id in self.annotations:
            # raise ValueError(f'Scene already has annotation with id: {annotation_model.id}')
            return self.annotations[annotation_model.id]

        annotation = AnnotationGraphicsItem(id=annotation_model.id, scale_provider=self.scale_provider,
                                            model=build_model(annotation_model),
                                            is_in_progress=False,
                                            removed_from_scene_callback=self.__on_annotation_removed_from_scene,
                                            slide_stats_provider=self)
        self.annotations[annotation_model.id] = annotation
        self.addItem(annotation)
        self.annotationModelAdded.emit(annotation_model)

        def on_pos_changed(p: QPoint):
            if annotation_model.id in self.annotations:
                annotation_model.geometry.origin_point = qpoint_to_tuple(p)
                self.annotationModelChanged.emit(annotation_model)

        annotation.signals.posChanged.connect(on_pos_changed)

        annotation.update()

        return annotation

    def edit_annotation(self, annotation_model: AnnotationModel) -> None:
        # annotation_model = annotation_model.copy(deep=True)
        if annotation_model.id not in self.annotations:
            # raise ValueError(f'Scene hasn\'t annotation with id: {annotation_model.id}')
            return
        annotation = self.annotations[annotation_model.id]
        annotation.set_model(build_model(annotation_model))
        self.annotationModelChanged.emit(annotation_model)
        # annotation.annotation_model = annotation_model
        annotation.update()

    def edit_with_copy(self, annotation_model: AnnotationModel) -> None:
        annotation_model = annotation_model.copy(deep=True)
        self.edit_annotation(annotation_model)

    def remove_annotations(self, ids: list) -> None:
        for id in ids:
            if id not in self.annotations:
                # raise ValueError(f'Scene hasn\'t annotation with id: {id}')
                continue
            annotation = self.annotations[id]
            self.removeItem(annotation)

    def select_annotations(self, ids: list) -> None:
        for i, annotation in self.annotations.items():
            annotation.setSelected(i in ids)

    def get_next_annotation_id(self) -> str:
        try:
            int_ids = [int(i) for i in self.annotations if i.isdigit()]
            next_id = max(int_ids) + 1 if int_ids else 1
            return str(next_id)
        except:
            next_id = len(self.annotations)
            return str(next_id)

    def clear(self) -> None:
        # pure clear doesn't call ItemSceneHasChanged for items!!!
        self.clear_annotations()
        super().clear()

    def clear_annotations(self) -> None:
        for i in list(self.annotations.values()):
            self.removeItem(i)

    def __on_update_stats(self, model: AnnotationModel):
        microns_per_pixel = self.get_microns_per_pixel()
        if model.geometry.is_distinguishable_from_point():
            annotation_type = model.geometry.annotation_type
            points = tuples_to_qpoints(model.geometry.points)
            display_attrs = model.text_graphics_view_config.display_attrs
            if annotation_type.has_length():
                length_px = calc_length(points[0], points[-1])
                length = length_px * microns_per_pixel
                stats = AnnotationStats(length_px=int(length_px), length=int(length))
                model.stats = stats
                length_attr = 'stats.length'
                if length_attr not in display_attrs:
                    display_attrs.append(length_attr)
            elif annotation_type.has_area():
                area_px = calc_geometry_area(model.geometry)
                area = area_px * microns_per_pixel ** 2
                stats = AnnotationStats(area_px=int(area_px), area=int(area))
                model.stats = stats
                area_attr = 'stats.area'
                if area_attr not in display_attrs:
                    display_attrs.append(area_attr)
        with slot_disconnected(self.annotationModelChanged, self.__on_update_stats):
            # TODO when syncing annotations between views, we need to consider views microns_per_pixel difference
            self.edit_annotation(model)
        # self.signals.annotationModelChanged.emit(model)

    def __on_annotation_removed_from_scene(self, annotation_id: str) -> None:
        del self.annotations[annotation_id]
        self.annotationModelsRemoved.emit([annotation_id])

    def __on_selection_changed(self) -> None:
        ids = [i.id for i in self.selectedItems() if isinstance(i, AnnotationGraphicsItem)]
        self.annotationModelsSelected.emit(ids)
