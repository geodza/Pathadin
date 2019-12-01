from contextlib import contextmanager
from functools import partial
from sys import getsizeof
from threading import RLock

import cachetools
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
    else:
        return getsizeof(item)


class DLRUCache(LRUCache):

    def __setitem__(self, key, value, cache_setitem=Cache.__setitem__):
        print(f"caching for key: {key} value of size: {sizeof_fmt(self.getsizeof(value))}")
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


def gcached(func_name):
    return cachetools.cached(cache_, key=partial(hashkey, func_name), lock=cache_lock)


@gcached("f")
def f(s):
    print(f"running f {s}")
    return s


if __name__ == '__main__':
    a1 = f(1)
    a2 = f(1)
    a3 = f(2)
    a4 = f(2)
    pass
