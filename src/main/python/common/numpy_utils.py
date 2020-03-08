from typing import Tuple, List, NamedTuple, Any

import numpy as np

NamedNdarray = Tuple[str, np.ndarray]


class NdarrayInfo(NamedTuple):
    shape: Tuple[int, ...]
    dtype: Any
    min_: Any
    max_: Any
    hist: np.ndarray
    bin_edges: np.ndarray
    hist_distribution: np.ndarray

    def _str(self, format="shape={shape}, dtype={dtype}, min={min_}, max={max_}, (bins;probs)=({bin_edges};{hist_distribution})"):
        return format.format_map(self._asdict())

    def __str__(self):
        return self._str()


class NdarraysInfo(NamedTuple):
    len_: int
    first: NdarrayInfo

    def _str(self, format="len: {len_}; first: shape={first.shape}, dtype={first.dtype}, min={first.min_}, max={first.max_}"):
        return format.format_map(self._asdict())

    def __str__(self):
        return self._str()


class NamedNdarrayInfo(NamedTuple):
    name: str
    info: NdarrayInfo

    def _str(self,
             format="name={name}, shape={info.shape}, dtype={info.dtype}, min={info.min_}, max={info.max_}, (bins;probs)=({info.bin_edges};{info.hist_distribution})"):
        return format.format_map(self._asdict())

    def __str__(self):
        return self._str()


class NamedNdarraysInfo(NamedTuple):
    len_: int
    first: NamedNdarrayInfo

    def _str(self,
             format="len: {len_}; first: name={first.name}, shape={first.info.shape}, dtype={first.info.dtype}, min={first.info.min_}, max={first.info.max_}"):
        return format.format_map(self._asdict())

    def __str__(self):
        return self._str()


def ndarray_info(ndarr: np.ndarray, bins=2) -> NdarrayInfo:
    hist, bin_edges = np.histogram(ndarr, bins)
    hist_distribution = hist / ndarr.size
    return NdarrayInfo(ndarr.shape, ndarr.dtype, ndarr.min(), ndarr.max(), hist, bin_edges, hist_distribution)


def ndarrays_info(ndarrays: List[np.ndarray]) -> NdarraysInfo:
    return NdarraysInfo(len(ndarrays), ndarray_info(ndarrays[0]))


def named_ndarray_info(named_ndarray: NamedNdarray) -> NamedNdarrayInfo:
    return NamedNdarrayInfo(named_ndarray[0], ndarray_info(named_ndarray[1]))


def named_ndarrays_info(named_ndarrays: List[NamedNdarray]) -> NamedNdarraysInfo:
    return NamedNdarraysInfo(len(named_ndarrays), named_ndarray_info(named_ndarrays[0]))


if __name__ == '__main__':
    # arr = np.random.rand(100, 100)
    arr = np.asarray([0, 1, 0, 1, 0, 0])
    info = ndarray_info(arr)
    print(ndarray_info(arr))
    print(ndarrays_info([arr]))
    print(named_ndarray_info(('abc', arr)))
    print(named_ndarrays_info([('abc', arr)]))
    print(info)
    print(info._asdict())

    print(np.can_cast(np.float32, float, casting='same_kind'))
    print(np.can_cast(np.uint8, float, casting='same_kind'))
    print(np.can_cast(float, np.uint8))
    print(np.can_cast(float, np.uint32))
    print(np.can_cast(float, np.uint64))
    print(np.can_cast(float, np.float32))
    print(np.can_cast(float, np.float64))

    print(np.can_cast(np.float16, np.uint8))
    print(np.can_cast(np.float16, np.uint32))
    print(np.can_cast(np.float16, np.uint64))
    print(np.can_cast(np.float16, float))
    print(np.can_cast(np.float16, np.float32))
    print(np.can_cast(np.float16, np.float64))
