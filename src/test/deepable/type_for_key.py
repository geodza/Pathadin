import unittest
from typing import NamedTuple

from dataclasses import dataclass
from pydantic import BaseModel

from deepable.convert import obj_from_dict, type_for_key
from deepable.core import deep_get, deep_replace


class TypeForKeyTest(unittest.TestCase):

	def test_dataclass(self):
		@dataclass
		class B:
			bb: str

		@dataclass
		class A:
			a: int
			b: B

		self.assertEqual(type_for_key(A, 'a'), int)
		self.assertEqual(type_for_key(A, 'b'), B)

	def test_named_tuple(self):
		class B(NamedTuple):
			bb: str

		class A(NamedTuple):
			a: int
			b: B

		self.assertEqual(type_for_key(A, 'a'), int)
		self.assertEqual(type_for_key(A, 'b'), B)

	def test_base_model(self):
		class B(BaseModel):
			bb: str

		class A(BaseModel):
			a: int
			b: B

		self.assertEqual(type_for_key(A, 'a'), int)
		self.assertEqual(type_for_key(A, 'b'), B)
