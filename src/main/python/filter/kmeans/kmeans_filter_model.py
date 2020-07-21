import json
from enum import unique, Enum
from typing import Optional, List, TypeVar, Generic

import dataclasses
from dataclasses import dataclass, field

from common.dataclass_utils import dataclass_fields
from filter.common.filter_data import ColumnDef, CsvExportConfig, FilterData


@unique
class KMeansInitType(str, Enum):
	kmeansPlusPlus = 'k-means++'
	random = 'random'
	ndarray = 'use NdarrayKMeansParams.ndarray to specify ndarray as start centroid centers'


@dataclass(frozen=True)
class KMeansParams:
	n_clusters: int = 3
	init: KMeansInitType = KMeansInitType.kmeansPlusPlus
	n_init: int = 5
	max_iter: int = 50
	tol: float = 1e-1
	random_state: Optional[int] = None


def default_kmeans_csv_export_config():
	# return None
	columns = [
		ColumnDef('annotation_id', 'id'),
		ColumnDef('annotation_label', 'label'),
		# ColumnDef('color', 'filter_results[attributes][histogram]', True)
		ColumnDef('color', 'filter_results.attributes.histogram', True)
	]
	return CsvExportConfig(columns=columns)

@dataclass(frozen=True)
class KMeansFilterData(FilterData):
	# filter_type: FilterType = field(default=FilterType.KMEANS, init=False)
	csv_export_config: Optional[CsvExportConfig] = field(default_factory=default_kmeans_csv_export_config)
	filter_type: str = field(default="kmeans")
	# filter_type: str = field(default="kmeans")
	# filter_type: ClassVar[str] = "kmeans"
	kmeans_params: KMeansParams = field(default_factory=KMeansParams)


@dataclass_fields
class KMeansParams_(KMeansParams):
	pass


@dataclass_fields
class KMeansFilterData_(KMeansFilterData):
	pass


@dataclass
class AA:
	aa: str


@dataclass
class BB(AA):
	bb: str


@dataclass
class A:
	a: AA


T = TypeVar('T', bound=AA)


@dataclass
class C(Generic[T]):
	cc: List[T]


if __name__ == '__main__':
	from dacite import from_dict, Config

	k = KMeansFilterData('1', '1')
	kdict = dataclasses.asdict(k)
	kjson = json.dumps(kdict)
	kdict2 = json.loads(kjson)
	print(kdict2)
	k2 = from_dict(KMeansFilterData, kdict2, config=Config(cast=[Enum]))
	print(k2)

	c = C[AA]([AA('1'), BB('2', '3')])

	d = dataclasses.asdict(c)

	с2 = from_dict(C[AA], d)
	print(с2)
	assert c == с2

# d = dataclasses.asdict(с)
# fd = KMeansFilterData("1", "1")
# print(fd)
# print(fd.dict())
# a = A(AA("123"))
# print(a)
# d = dataclasses.asdict(a)
# from dacite import from_dict
#
# a2 = from_dict(A, d)
# print(a2)
# assert a == a2
