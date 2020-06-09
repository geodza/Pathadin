import json
from abc import abstractmethod, ABC
from enum import Enum
from json import JSONEncoder, JSONDecoder
from json.encoder import JSONEncoder
from typing import Any, TypeVar, Generic, Optional, List, Callable

from common.file_utils import make_if_not_exists


def read(json_path: str) -> Any:
	with open(json_path, "r") as f:
		val = json.loads(f.read())
		return val


def write(json_path: str, val: Any, cls=json.JSONEncoder, mode: str = "w") -> None:
	make_if_not_exists(json_path)
	with open(json_path, mode) as f:
		json.dump(val, f, indent=4, cls=cls)


T = TypeVar("T")


class JSONEncoderFactory(ABC, Generic[T]):
	@abstractmethod
	def create_encoder(self, o: T) -> Optional[JSONEncoder]:
		pass


class JSONDecoderFactory(ABC):
	@abstractmethod
	def create_decoder(self, d: dict) -> JSONDecoder:
		pass


class CompositeJSONEncoder(JSONEncoder):

	def __init__(self, factories: List[JSONEncoderFactory]):
		self.factories = factories

	def find_encoder(self, o: Any) -> JSONEncoder:
		for f in self.factories:
			d = f.create_encoder(o)
			if d is not None:
				return d
		raise ValueError(f"CompositeJSONEncoder. No appropriate factory found for {o} in {self.factories}")

	def default(self, o: Any) -> Any:
		e = self.find_encoder(o)
		if e is not None:
			return e.default(o)
		return super().default(o)


class CompositeJSONDecoder(JSONDecoder):

	def __init__(self, factories: List[JSONDecoderFactory]):
		self.factories = factories

	def find_decoder(self, d: dict) -> JSONDecoder:
		for f in self.factories:
			decoder = f.create_decoder(d)
			if decoder is not None:
				return decoder
		raise ValueError(f"CompositeJSONDecoder. No appropriate factory found for {d} in {self.factories}")


class StrEnumJSONEncoder(JSONEncoder):

	def default(self, o: Any) -> Any:
		if isinstance(o, str) and isinstance(o, Enum):
			return o.value

		return super().default(o)

# class JSONEncoderT(JSONEncoder, ABC, Generic[T]):
# 	def default(self, o: T) -> Any:
# 		return super().default(o)
class TypesBasedJSONEncoderFactory(JSONEncoderFactory):

	def __init__(self, types, encoder: JSONEncoder):
		self.types = types
		self.encoder = encoder

	def create_encoder(self, o: T) -> Optional[JSONEncoder]:
		if isinstance(o, self.types):
			return self.encoder
		else:
			return None

if __name__ == '__main__':
	def f(d):
		print(d)

	o = json.loads('{"a":1, "b":{"bb":2}}', object_hook=f)
	print(o)
