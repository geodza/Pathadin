# https://tsilva.me/how-to-write-a-debouncer-function-in-python/
from typing import Callable, TypeVar, Any

from PyQt5.QtCore import QTimer

T = TypeVar('T')


def debounce_one_arg_signal(wait_sec: float, func: Callable[[T], Any]) -> Callable[[T], Any]:
    scheduled_timer = QTimer()
    scheduled_timer.setSingleShot(True)

    def debounced_func(arg: T):

        def f():
            # print(arg)
            func(arg)

        try:
            scheduled_timer.timeout.disconnect()
        except:
            pass

        scheduled_timer.start(int(wait_sec * 1000))
        scheduled_timer.timeout.connect(f)

    return debounced_func
