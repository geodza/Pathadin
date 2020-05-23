from collections import Iterable
from concurrent.futures._base import Future
from contextlib import contextmanager
from functools import partial
from sys import getsizeof
from threading import RLock

import cachetools
import numpy as np
from PIL import Image
from PyQt5.QtGui import QImage
from cachetools import LRUCache, Cache
from cachetools.keys import hashkey

cache_size_in_bytes = 4 * 2 ** 30


# def debug_cache(cache: LRUCache):
#     def wrapper(cache, key, value, cache_setitem=Cache.__setitem__):
#         print(f"caching for key: {key} value of size: {cache.getsizeof(value)}")
#         f(cache, key, value, cache_setitem)
#
#     Cache.__setitem__ = types.MethodType(wrapper, cache)
#     return cache

# https://stackoverflow.com/questions/1094841/reusable-library-to-get-human-readable-version-of-file-size
def sizeof_fmt(num, suffix='B'):
    for unit in ['', 'Ki', 'Mi', 'Gi', 'Ti', 'Pi', 'Ei', 'Zi']:
        if abs(num) < 1024.0:
            return "%3.1f%s%s" % (num, unit, suffix)
        num /= 1024.0
    return "%.1f%s%s" % (num, 'Yi', suffix)


def sizeof(item):
    if isinstance(item, Image.Image):
        img_pixel_size = item.width * item.height * len(item.getbands()) * 8
        img_object_size = getsizeof(item)
        return img_pixel_size + img_object_size
    elif isinstance(item, QImage):
        img_size = item.width() * item.height() * item.depth() / 8
        img_object_size = getsizeof(img_size)
        return img_size + img_object_size
    elif isinstance(item, np.ndarray):
        return item.nbytes
    elif isinstance(item, Iterable) and not isinstance(item, str):
        items = list(item)
        size = 0
        for i in items:
            size += sizeof(i)
        return size
        # sizes = [sizeof(i) for i in items]
        # return sum(sizes)
    else:
        return getsizeof(item)


class DLRUCache(LRUCache):

    def __setitem__(self, key, value, cache_setitem=Cache.__setitem__):
        # print(f"caching with size {sizeof_fmt(self.getsizeof(value))} for key: {key} value")
        super().__setitem__(key, value, cache_setitem)


cache_ = DLRUCache(cache_size_in_bytes, getsizeof=sizeof)


# cache_ = debug_cache(cache_)
# cache_.__setitem__("s", 123)
# cache_["s"] = 1

# https://stackoverflow.com/questions/16740104/python-lock-with-statement-and-timeout
@contextmanager
def acquire_timeout(lock, timeout):
    result = lock.acquire(timeout=timeout)
    yield result
    if result:
        lock.release()


cache_lock = RLock()
pixmap_cache_lock = RLock()


def cache_key_func(func_name):
    return partial(hashkey, func_name)


# def gcached(func_name,*args):
#     return cachetools.cached(cache_, key=partial(hashkey, func_name), lock=cache_lock)

def gcached(method):
    return cachetools.cached(cache_, key=partial(hashkey, method.__name__), lock=cache_lock)(method)


@gcached
def f(s):
    print(f"running f {s}")
    return s


if __name__ == '__main__':
    a1 = f(1)
    a2 = f(1)
    a3 = f(2)
    a4 = f(2)
    pass


def build_global_pending_key(key: str):
    return 'pending__{}'.format(key)


def add_to_global_pending(key: str, future: Future):
    # print("add_to_global_pending", key)
    cache_[build_global_pending_key(key)] = future


def get_from_global_pending(key: str) -> Future:
    return cache_[build_global_pending_key(key)]


def is_in_global_pending(key: str):
    return build_global_pending_key(key) in cache_


def remove_from_global_pending(key: str):
    # print("remove_from_global_pending", key)
    cache_.pop(build_global_pending_key(key), None)


def closure_nonhashable(hash_prefix: str, nonhashable_input, func):
    # def decor(method):
    #     return cachetools.cached(cache_, key=partial(hashkey, method.__name__, hash_prefix), lock=cache_lock)(method)

    def w(*args, **kwargs):
        return func(nonhashable_input, *args, **kwargs)

    cached_w = cachetools.cached(cache_, key=partial(hashkey, func.__name__, hash_prefix), lock=cache_lock)(w)

    return cached_w
