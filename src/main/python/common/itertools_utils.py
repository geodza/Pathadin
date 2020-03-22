import itertools
from typing import TypeVar, Iterable, Tuple, Callable, Any

T = TypeVar('T')
K = TypeVar('K')
C = TypeVar('C')


def batchify(items: Iterable[T], batch_size: int, batches_mapper: Callable[[Iterable[T]], Any] = None) -> Iterable[Iterable[T]]:
    # enumerate items and group them by batch index
    item_groups = itertools.groupby(enumerate(items), lambda t: t[0] // batch_size)
    # extract items from enumeration tuples
    if batches_mapper:
        item_batches = (batches_mapper(t[1] for t in group_items) for key, group_items in item_groups)
    else:
        item_batches = ((t[1] for t in group_items) for key, group_items in item_groups)
    return item_batches


def do_by_batches(items: Iterable[T], batch_size, func: Callable[[Iterable[T]], None]) -> None:
    items_batches = batchify(items, batch_size)
    for batch in items_batches:
        func(batch)


def groupbyformat(items: Iterable[T], key_format: str) -> Iterable[Tuple[str, Iterable[T]]]:
    def groupby_func(item: T) -> str:
        key = key_format.format_map(item._asdict())
        return key

    return itertools.groupby(items, groupby_func)


def map_inside_group(groups: Iterable[Tuple[K, T]], map_func: Callable[[T], C]) -> Iterable[Tuple[K, C]]:
    for key, group_items in groups:
        c = map_func(group_items)
        yield (key, c)


def peek(iterable: Iterable[T]) -> Tuple[T, Iterable[T]]:
    first = next(iterable)
    restored = itertools.chain([first], iterable)
    return (first, restored)
