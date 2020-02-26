import itertools
from typing import Iterable, Callable, Any

from common.itertools_utils import batchify

if __name__ == '__main__':
    print(list(batchify(range(10), 3, tuple)))
    # print(list(batchify([1, 100, 3, 5, 6, 90, 43], 3)))
    for i in batchify([1, 9, 3, 5, 2, 4, 2], 4):
        print(list(i))
    print(list(batchify([1, 9, 3, 5, 2, 4, 2], 4, tuple)))
    # [(1, 9, 3, 5), (2, 4, 2)]
    print(list(batchify([1, 9, 3, 5, 2, 4, 2], 4, list)))
    # [[1, 9, 3, 5], [2, 4, 2]]

    print(list(batchify([1, 100, 3, 5, 6, 90, 43], 3, tuple)))
    print(list(batchify([1, 100, 3, 5, 6, 90, 43], 2, tuple)))
    print(list(batchify([1, 100, 3, 5, 6, 90, 43], 1, tuple)))
    print(list(batchify([1, 100, 3, 5, 6, 90, 43], 3, list)))
    print(list(batchify([1, 1, 100, 3, 5, 6, 6, 90, 90, 43], 3, set)))
