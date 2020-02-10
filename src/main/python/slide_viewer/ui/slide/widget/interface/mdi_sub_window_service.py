from abc import ABC, abstractmethod
from enum import unique, auto, Enum

from PyQt5.QtCore import pyqtSignal, pyqtBoundSignal
from PyQt5.QtWidgets import QMdiSubWindow


@unique
class SyncOption(Enum):
    all = auto()
    view_transform = auto()
    grid_visible = auto()
    grid_size = auto()
    file_path = auto()
    background_brush = auto()
    annotations = auto()
    annotation_filter = auto()

    @staticmethod
    def single_options():
        return set(SyncOption) - {SyncOption.all}


class SubWindowService(ABC):
    isSyncChanged = pyqtSignal(SyncOption)

    @abstractmethod
    def add_sub_window(self) -> QMdiSubWindow:
        pass

    @abstractmethod
    def tile_sub_windows(self) -> None:
        pass

    @property
    @abstractmethod
    def sub_window_activated(self) -> pyqtBoundSignal:
        pass

    @property
    @abstractmethod
    def sub_window_slide_path_changed(self) -> pyqtBoundSignal(str):
        pass

    @property
    @abstractmethod
    def active_sub_window(self) -> QMdiSubWindow:
        pass

    @property
    @abstractmethod
    def has_sub_windows(self) -> bool:
        pass

    @abstractmethod
    def get_sync_state(self, option: SyncOption) -> bool:
        pass

    @abstractmethod
    def set_sync_state(self, option: SyncOption, sync: bool) -> None:
        pass
