import itertools
from typing import Iterable, Tuple, Callable, TypeVar

T1 = TypeVar("T1")
K1 = TypeVar("K1")
C1 = TypeVar("C1")


def groupbyformat(items: Iterable[T1], key_format: str) -> Iterable[Tuple[str, Iterable[T1]]]:
    def groupby_func(item: T1) -> str:
        key = key_format.format_map(item._asdict())
        return key

    return itertools.groupby(items, groupby_func)


def map_inside_group(groups: Iterable[Tuple[K1, T1]], map_func: Callable[[T1], C1]) -> Iterable[Tuple[K1, C1]]:
    for key, group_items in groups:
        c = map_func(group_items)
        yield (key, c)
