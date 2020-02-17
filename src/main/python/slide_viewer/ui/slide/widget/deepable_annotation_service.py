from collections import OrderedDict
from typing import List, Dict, Tuple

from PyQt5.QtCore import QObject, pyqtBoundSignal, pyqtSignal

from common_qt.abcq_meta import ABCQMeta
from deepable.core import toplevel_keys
from deepable_qt.deepable_tree_model import DeepableTreeModel
from img.filter.base_filter import FilterResults2, ThresholdFilterResults
from img.filter.keras_model import KerasModelFilterResults
from img.filter.kmeans_filter import KMeansFilterResults
from img.filter.nuclei import NucleiFilterResults
from img.filter.positive_pixel_count import PositivePixelCountFilterResults
from slide_viewer.ui.odict.deep.model import AnnotationModel
from slide_viewer.ui.slide.graphics.item.annotation.model import AnnotationStats
from slide_viewer.ui.slide.widget.interface.annotation_service import AnnotationService

ituple = Tuple[int, int]


# It is important to update tree annotations_tree_model from main gui thread and not from thread-pool task thread
# It is important to update data of annotations_tree_model only through annotations_tree_model interface
# We copy annotation, edit it and finally change annotations_tree_model through annotations_tree_model interface


def build_text_filter_results(filter_results: FilterResults2) -> OrderedDict:
    if isinstance(filter_results, (KMeansFilterResults, ThresholdFilterResults)):
        filter_results_dict = OrderedDict({'histogram_html_text': filter_results.histogram_html})
    elif isinstance(filter_results, NucleiFilterResults):
        nuclei_count_text = f"nuclei count: {filter_results.nuclei_count}"
        filter_results_dict = OrderedDict({'nuclei_count_text': nuclei_count_text})
    elif isinstance(filter_results, PositivePixelCountFilterResults):
        try:
            stats_dict = filter_results.stats._asdict()
            stats_html_text = '<br/>'.join([f'{k}: {round(v, 3)}' for k, v in stats_dict.items()])
            filter_results_dict = OrderedDict({'stats_html_text': stats_html_text})
        except:
            filter_results_dict = OrderedDict({'stats_html_text': "error, try to move annotation or to change filter params"})
    elif isinstance(filter_results, KerasModelFilterResults):
        filter_results_dict = OrderedDict()
    else:
        raise ValueError()
    return filter_results_dict


class DeepableAnnotationService(QObject, AnnotationService, metaclass=ABCQMeta):
    added = pyqtSignal(AnnotationModel)
    edited = pyqtSignal(str, AnnotationModel)
    deleted = pyqtSignal(list)
    selected = pyqtSignal(list)

    def __init__(self, root: DeepableTreeModel) -> None:
        self.root = root
        self.annotation_label_template: str = 'annotation_{}'
        self.root.objectsRemoved.connect(self.__on_removed)
        self.root.objectsChanged.connect(self.__on_changed)
        self.root.objectsInserted.connect(self.__on_added)
        super().__init__()

    def get_first_point(self, id_: str) -> ituple:
        return self.get(id_).geometry.points[0]

    def add_point(self, id_: str, p: ituple) -> None:
        model = self.get(id_).copy(deep=True)
        model.geometry.points.append(p)
        self.root[id_] = model

    # add or update
    def add_or_edit(self, id_: str, model: AnnotationModel) -> AnnotationModel:
        self.root[id_] = model
        return self.get(id_)

    def add_or_edit_with_copy(self, id_: str, model: AnnotationModel) -> AnnotationModel:
        # with slot_disconnected(self.root.objectsChanged, self.__on_changed):
        model_copy = model.copy(deep=True)
        self.root[id_] = model_copy
        # self.edited_signal().emit(id_, model_copy)
        return model_copy

    def add_or_edit_with_copy_without_filter(self, id_: str, model: AnnotationModel) -> AnnotationModel:
        # with slot_disconnected(self.root.objectsChanged, self.__on_changed):
        model_copy = model.copy(deep=True)
        model_copy.filter_results = None
        model_copy.filter_id = None
        model_copy.filter_level = None
        original_model = self.get(id_)
        if original_model:
            original_model_dict = original_model.dict()
            model_copy_dict = model_copy.dict(exclude={'filter_results', 'filter_id', 'filter_level'})
            original_model_dict.update(model_copy_dict)
            merged_model = AnnotationModel.parse_obj(original_model_dict)
        else:
            merged_model = model_copy
        self.root[id_] = merged_model
        # self.edited_signal().emit(id_, merged_model)
        return merged_model

    def edit_origin_point(self, id_: str, p: ituple) -> None:
        model = self.get(id_).copy(deep=True)
        model.geometry.origin_point = p
        self.root[id_] = model

    # def edit_origin_point_with_delay(self, id_: str, p: ituple) -> None:
    #     with slot_disconnected(self.root.objectsChanged, self.__on_changed):
    #         self.edit_origin_point(id_, p)
    #
    #         def f():
    #             self.edited_signal().emit(id_, self.get(id_))
    #
    #         QTimer.singleShot(100, f)

    def edit_last_point(self, id_: str, p: ituple) -> None:
        # print("edit last point")
        model = self.get(id_).copy(deep=True)
        model.geometry.points[-1] = p
        self.root[id_] = model

    def edit_filter_results(self, id_: str, filter_results: FilterResults2) -> None:
        text_filter_results = build_text_filter_results(filter_results)
        if str(self.get(id_).filter_results) != str(text_filter_results):
            # model = self.get(id_).copy(deep=True)
            # model.filter_results = text_filter_results
            self.root[f'{id_}.filter_results'] = text_filter_results
            # self.root[id_] = model

    def edit_stats(self, id_: str, stats: AnnotationStats) -> None:
        if str(self.get(id_).stats) != str(stats):
            # model = self.get(id_).copy(deep=True)
            # model.stats = stats
            self.root[f'{id_}.stats'] = stats
            # self.root[id_] = model

    def get(self, id_: str) -> AnnotationModel:
        return self.root[id_]

    def get_dict(self) -> Dict[str, AnnotationModel]:
        return {id_: self.root[id_] for id_ in self.root}

    def has(self, id_: str) -> bool:
        return id_ in self.root

    def delete(self, ids: List[str]) -> None:
        for id_ in ids:
            del self.root[id_]

    def delete_if_exist(self, ids: List[str]) -> None:
        for id_ in ids:
            if self.has(id_):
                del self.root[id_]

    def delete_all(self) -> None:
        self.root.clear()

    def add(self, model: AnnotationModel) -> AnnotationModel:
        model.id = self.get_next_id()
        model.label = self.annotation_label_template.format(model.id)
        self.root[model.id] = model
        return model

    def add_copy(self, model: AnnotationModel) -> AnnotationModel:
        model_copy = model.copy(deep=True)
        self.root[model_copy.id] = model_copy
        return model_copy

    def added_signal(self) -> pyqtBoundSignal(AnnotationModel):
        return self.added

    def edited_signal(self) -> pyqtBoundSignal(str, AnnotationModel):
        return self.edited

    def deleted_signal(self) -> pyqtBoundSignal(list):
        return self.deleted

    def get_next_id(self) -> str:
        try:
            int_ids = [int(id_) for id_ in self.root if id_.isdigit()]
            next_id = max(int_ids) + 1 if int_ids else 1
            return str(next_id)
        except:
            next_id = len(self.root) + 1
            return str(next_id)

    def __on_removed(self, keys: List[str]):
        selected_toplevel_keys = toplevel_keys(keys) & set(keys)
        self.deleted_signal().emit(list(selected_toplevel_keys))

    def __on_added(self, keys: List[str]):
        for toplevel_key in toplevel_keys(keys):
            # print("on_added", toplevel_key)
            self.added_signal().emit(self.get(toplevel_key))

    def __on_changed(self, keys: List[str]):
        for toplevel_key in toplevel_keys(keys):
            # print(f"keys: {keys} top_level_key: {toplevel_key} onChanged")
            self.edited_signal().emit(toplevel_key, self.get(toplevel_key))
