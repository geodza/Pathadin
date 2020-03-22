import random
from typing import List, TypeVar, Tuple, Iterable

import numpy as np

T = TypeVar('T')
S = TypeVar('S')


def shuffle_lists(X: List[T], Y: List[S]) -> Tuple[List[T], List[S]]:
    tuples = list(zip(X, Y))
    random.shuffle(tuples)
    X_, Y_ = zip(*tuples)
    return X_, Y_


def shuffle_list(X: List[T], indices=Iterable[int]) -> List[T]:
    X_ = [X[i] for i in indices]
    return X_


def shuffle_ndarrays(X: np.ndarray, Y: np.ndarray) -> Tuple[np.ndarray, np.ndarray]:
    indices = np.arange(len(X))
    np.random.shuffle(indices)
    X_ = X[indices]
    Y_ = Y[indices]
    return X_, Y_
