from contextlib import contextmanager


@contextmanager
# https://gist.github.com/durden/5060373
def slot_disconnected(signal, slot):
    """
    Create context to perform operations with given slot disconnected from
    given signal and automatically connected afterwards.
    usage:
        with slot_disconnected(chkbox.stateChanged, self._stateChanged):
            foo()
            bar()
    """
    # try:
    signal.disconnect(slot)
    yield
    signal.connect(slot)
    # except TypeError:
    #     yield
