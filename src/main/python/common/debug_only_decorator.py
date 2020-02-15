from typing import Callable

def debug_only(debug_: bool = False) -> Callable[[Callable], Callable]:
    def debug_only_wrap(func):
        def func_wrap(*args, **kwargs):
            if debug_:
                func(*args, **kwargs)

        return func_wrap

    return debug_only_wrap
