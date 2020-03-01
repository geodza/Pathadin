from typing import Tuple, List

import numpy as np

NamedNdarray = Tuple[str, np.ndarray]


def print_named_ndarrays_info(named_ndarrays: List[NamedNdarray]) -> None:
    print(f"named ndarrays count: {len(named_ndarrays)}")
    if len(named_ndarrays):
        name, ndarr = named_ndarrays[0]
        print(f"1-st array (name,shape,dtype,min,max): {(name, ndarr.shape, ndarr.dtype, min(ndarr), max(ndarr))}")


def print_ndarrays_info(ndarrays: List[np.ndarray]) -> None:
    print(f"ndarrays count: {len(ndarrays)}")
    if len(ndarrays):
        ndarr = ndarrays[0]
        print(f"1-st array (shape,dtype,min,max): {(ndarr.shape, ndarr.dtype, min(ndarr), max(ndarr))}")
