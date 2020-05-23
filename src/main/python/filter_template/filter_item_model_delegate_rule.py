from typing import NamedTuple

from common_qt.mvc.model.delegate.item_model_delegate import AbstractItemModelDelegate
from deepable_qt.model.deepable_model_index import DeepableQModelIndex

T = DeepableQModelIndex


class FilterItemModelDelegateRule(NamedTuple):
	source: type
	target: AbstractItemModelDelegate[T]
