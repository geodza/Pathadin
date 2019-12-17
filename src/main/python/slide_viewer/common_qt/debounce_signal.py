# https://tsilva.me/how-to-write-a-debouncer-function-in-python/
from typing import Callable, TypeVar, Any

from PyQt5.QtCore import QTimer

T = TypeVar('T')
T2 = TypeVar('T2')
T3 = TypeVar('T3')


def debounce_one_arg_slot(wait_sec: float, func: Callable[[T], Any]) -> Callable[[T], Any]:
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


def debounce_two_arg_slot(wait_sec: float, func: Callable[[T, T2], Any]) -> Callable[[T, T2], Any]:
    scheduled_timer = QTimer()
    scheduled_timer.setSingleShot(True)

    def debounced_func(arg: T, arg2: T2):

        def f():
            # print(arg)
            func(arg, arg2)

        try:
            scheduled_timer.timeout.disconnect()
        except:
            pass

        scheduled_timer.start(int(wait_sec * 1000))
        scheduled_timer.timeout.connect(f)

    return debounced_func


def debounce_three_arg_slot(wait_sec: float, func: Callable[[T, T2, T3], Any]) -> Callable[[T, T2, T3], Any]:
    scheduled_timer = QTimer()
    scheduled_timer.setSingleShot(True)

    def debounced_func(arg: T, arg2: T2, arg3: T3):

        def f():
            # print(arg)
            func(arg, arg2, arg3)

        try:
            scheduled_timer.timeout.disconnect()
        except:
            pass

        scheduled_timer.start(int(wait_sec * 1000))
        scheduled_timer.timeout.connect(f)

    return debounced_func


def debounce_one_arg_slot_wrap(wait_sec: float):
    def wrap(func):
        return debounce_one_arg_slot(wait_sec, func)

    return wrap


def debounce_two_arg_slot_wrap(wait_sec: float):
    def wrap(func):
        return debounce_two_arg_slot(wait_sec, func)

    return wrap


def debounce_three_arg_slot_wrap(wait_sec: float):
    def wrap(func):
        return debounce_three_arg_slot(wait_sec, func)

    return wrap


def debounce_slot(wait_sec: float, func: Callable[..., Any]) -> Callable[..., Any]:
    scheduled_timer = QTimer()
    scheduled_timer.setSingleShot(True)

    def debounced_func(*args, **kwargs):

        def f():
            # print(arg)
            func(*args, **kwargs)

        try:
            scheduled_timer.timeout.disconnect()
            # print(f'canceling {id(func)} {id(scheduled_timer)}')
        except:
            pass

        scheduled_timer.start(int(wait_sec * 1000))
        scheduled_timer.timeout.connect(f)

    return debounced_func


def debounce_slot_wrap(wait_sec: float):
    def wrap(func):
        return debounce_slot(wait_sec, func)

    return wrap
