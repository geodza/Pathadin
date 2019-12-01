def closure_factory(*args):
    def closure(func):
        def wrap_():
            func(*args)

        return wrap_

    return closure

