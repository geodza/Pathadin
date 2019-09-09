import os


def make_if_not_exists(filepath: str) -> None:
    d = os.path.dirname(filepath)
    if d and not os.path.exists(d):
        os.makedirs(d)
