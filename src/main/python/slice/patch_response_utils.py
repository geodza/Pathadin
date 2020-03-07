from typing import Tuple, Iterable

import numpy as np

from common.itertools_utils import map_inside_group, groupbyformat
from ndarray_persist.ndarray_persist_utils import NamedNdarray
from slice.model.patch_image import PatchImageIterable
from slice.model.patch_response import PatchResponseIterable

PatchResponseGroup = Tuple[str, PatchResponseIterable]


def stack_patch_responses_images(patch_responses: PatchResponseIterable) -> np.ndarray:
    imgs = [pr.img.ndarray for pr in patch_responses]
    if len(imgs) == 1:
        ndarray = imgs[0]
    else:
        ndarray = np.vstack(imgs)
    return ndarray


def patch_responses_to_named_ndarrays(patch_responses: PatchResponseIterable, group_key_format: str) -> Iterable[NamedNdarray]:
    patch_responses_groups = groupbyformat(patch_responses, group_key_format)
    image_groups = map_inside_group(patch_responses_groups, stack_patch_responses_images)
    # image_groups = list(image_groups)
    return image_groups


def stack_patch_images(patch_images: PatchImageIterable) -> np.ndarray:
    imgs = [p[2].ndarray for p in patch_images]
    ndarray = np.vstack(imgs)
    return ndarray


def patch_images_to_named_ndarrays(patch_images: PatchImageIterable, group_key_format: str) -> Iterable[NamedNdarray]:
    patch_images_groups = groupbyformat(patch_images, group_key_format)
    image_groups = map_inside_group(patch_images_groups, stack_patch_images)
    # image_groups = list(image_groups)
    return image_groups
