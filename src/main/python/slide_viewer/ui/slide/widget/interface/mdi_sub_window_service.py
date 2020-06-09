from abc import ABC, abstractmethod

from PyQt5.QtCore import pyqtSignal, pyqtBoundSignal
from PyQt5.QtWidgets import QMdiSubWindow

from slide_viewer.ui.slide.widget.sync.sync_option import SyncOption


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
