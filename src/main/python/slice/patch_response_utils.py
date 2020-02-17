from typing import Tuple, Iterable

import numpy as np

from common.itertools_utils import map_inside_group, groupbyformat
from ndarray_persist.ndarray_persist_utils import NamedNdarray
from slice.model.patch_response import PatchResponseIterable

PatchResponseGroup = Tuple[str, PatchResponseIterable]


def collect_patch_responses_images_to_ndarray(patch_responses: PatchResponseIterable) -> np.ndarray:
    imgs = [pr.img.ndarray for pr in patch_responses]
    ndarray = np.stack(imgs)
    return ndarray


def collect_images_inside_groups(groups: Iterable[PatchResponseGroup]) -> Iterable[Tuple[str, np.ndarray]]:
    return map_inside_group(groups, collect_patch_responses_images_to_ndarray)


def group_patch_responses(patch_responses: PatchResponseIterable, group_key_format: str) -> Iterable[PatchResponseGroup]:
    return groupbyformat(patch_responses, group_key_format)


def collect_responses_to_named_ndarrays(patch_responses: PatchResponseIterable, group_key_format: str) -> Iterable[NamedNdarray]:
    response_groups = groupbyformat(patch_responses, group_key_format)
    image_groups = collect_images_inside_groups(response_groups)
    # image_groups = list(image_groups)
    return image_groups
