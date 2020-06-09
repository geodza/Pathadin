import unittest
from typing import NamedTuple

from dataclasses import dataclass

from deepable.core import deep_get, deep_replace


class ObjFromDictTest(unittest.TestCase):

	def test_obj_from_dict(self):
		@dataclass
		class C:
			ccc: str

		class B(NamedTuple):
			bb: str
			c: C

		@dataclass
		class A:
			a: int
			b: B

		d1 = {"a": 1, "b": {"bb": "123", "c": {"ccc": "333"}}}
		# o1 = obj_from_dict(d1, kwargs_init_object_hook, A)
		# self.assertEqual(o1, A(1, B("123", C("333"))))
