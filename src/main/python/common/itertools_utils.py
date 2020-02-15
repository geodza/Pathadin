import itertools
from typing import TypeVar, Iterable, Tuple, Callable


def batchify(generator, batch_size):
    items = []
    for i, item in enumerate(generator):
        items.append(item)
        if (i + 1) % batch_size == 0:
            yield items
            items = []
    if items:
        yield items


def star_batchify(generator, batch_size):
    items = []
    for i, item in enumerate(generator):
        items.extend(item)
        if (i + 1) % batch_size == 0:
            tuple_length = len(item)
            yield tuple(items[j:None:tuple_length] for j in range(tuple_length))
            items = []
    if items:
        tuple_length = len(items) // batch_size
        yield tuple(items[j:None:tuple_length] for j in range(tuple_length))


def tuple_map(func, tuple_generator):
    results = []
    for tuple_ in tuple_generator:
        for item in tuple_:
            res = func(item)
            results.append(res)
        yield tuple(results)
        results = []


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