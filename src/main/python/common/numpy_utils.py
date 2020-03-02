from typing import Tuple, List, Union, NamedTuple

import numpy as np

NamedNdarray = Tuple[str, np.ndarray]

# class NdarrayInfo(NamedTuple):
#     shape:Tuple[int,...]
#     shape:Tuple[int,...]


def print_named_ndarrays_info(named_ndarrays: List[NamedNdarray]) -> None:
    print(f"named ndarrays count: {len(named_ndarrays)}")
    if len(named_ndarrays):
        name, ndarr = named_ndarrays[0]
        print(f"1-st array (name,shape,dtype,min,max): {(name, ndarr.shape, ndarr.dtype, ndarr.min(), ndarr.max())}")




def print_ndarrays_info(ndarrays: Union[np.ndarray, List[np.ndarray]]) -> None:
    print(f"ndarrays count: {len(ndarrays)}")
    if len(ndarrays):
        if isinstance(ndarrays, np.ndarray):
            hist, edges = np.histogram(ndarrays, 5)
            distribution = hist / ndarrays.size
            print(f"ndarrays (shape,dtype,min,max): {(ndarrays.shape, ndarrays.dtype, ndarrays.min(), ndarrays.max())}")
            # TODO format float
            print(f"ndarrays distribution (bins,prob): {(list(edges),list(distribution))}")
        else:
            ndarr = ndarrays[0]
            print(f"1-st ndarray (shape,dtype,min,max): {(ndarr.shape, ndarr.dtype, ndarr.min(), ndarr.max())}")
