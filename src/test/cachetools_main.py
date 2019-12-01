from functools import partial
from sys import getsizeof
import numpy as np
from PIL import Image
from cachetools import cached, LRUCache
from cachetools.keys import hashkey

cache_ = LRUCache((96 + 10 * 4) * 2, getsizeof=getsizeof)


@cached(cache_, partial(hashkey, 'f'))
def f(s):
    print(f"running f for : {s}")
    return np.zeros(s, dtype=np.uint32)


@cached(cache_, partial(hashkey, 'g'))
def g(s):
    print(f"running g for : {s}")
    return np.ones(s, dtype=np.uint32)


@cached(cache_, partial(hashkey, 'img'))
def img(s):
    print(f"running img for : {s}")
    return Image.new("L", s)




if __name__ == "__main__":
    a1 = f(5)
    a1_ = f(2)
    a2 = f(5)
    a3 = g(5)
    a4 = g(5)
    a5 = f(5)
    a6 = f(10)
    print(getsizeof(np.empty(1, dtype=np.uint8)))
    print(getsizeof(np.empty(2, dtype=np.uint8)))
    print(getsizeof(np.empty(1, dtype=np.uint32)))
    print(getsizeof(np.empty(2, dtype=np.uint32)))
    print(getsizeof(np.empty(1, dtype=np.double)))
    print(getsizeof(np.empty(2, dtype=np.double)))
    img1 = img((100, 100))
    print(getsizeof(img((1, 1))))
    print(getsizeof(img((10, 10))))
    print(getsizeof(img((100, 100))))
    pass
