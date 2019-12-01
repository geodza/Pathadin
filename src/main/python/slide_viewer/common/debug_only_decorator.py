from typing import Callable

from slide_viewer.config import debug


def debug_only(debug_: bool = debug) -> Callable[[Callable], Callable]:
    def debug_only_wrap(func):
        def func_wrap(*args, **kwargs):
            if debug_:
                func(*args, **kwargs)

        return func_wrap

    return debug_only_wrap
