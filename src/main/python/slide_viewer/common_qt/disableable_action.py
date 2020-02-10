import typing
from typing import Callable, Iterable

from PyQt5.QtCore import QObject, pyqtSignal
from PyQt5.QtWidgets import QAction
from dataclasses import dataclass, InitVar

from slide_viewer.common_qt.abcq_meta import ABCQMeta
from slide_viewer.common_qt.disableable import Disableable


def subscribe_disableable(disability_signals: Iterable[pyqtSignal], enability_resolver: Callable[[], bool],
                          disableable: Disableable):
    def on_disability_update(*args):
        # print(f"disability_signal! set disabled: {not enability_resolver()}", )
        disableable.setDisabled(not enability_resolver())

    for signal in disability_signals:
        signal.connect(on_disability_update)

    on_disability_update()


@dataclass()
class DisableableAction(QAction, Disableable, metaclass=ABCQMeta):
    parent_: InitVar[typing.Optional[QObject]]
    disability_signals: InitVar[Iterable[pyqtSignal]]
    enability_resolver: InitVar[Callable[[], bool]]

    def __post_init__(self, parent_: typing.Optional[QObject], disability_signals: Iterable[pyqtSignal],
                      enability_resolver: Callable[[], bool]):
        QAction.__init__(self, parent_)

        subscribe_disableable(disability_signals, enability_resolver, self)

# a = DisableableAction(None, [], lambda: True)
# print(a)
