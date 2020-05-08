import unittest

from dataclasses import dataclass

from deepable.core import deep_get, deep_replace


class DeepGetTest(unittest.TestCase):

	def test_dict_deep_replace(self):
		d1 = {"a": {"b": {"c": 1}}}
		self.assertEqual({"a": {"b": {"c": 2}}}, deep_replace(d1, "a.b.c", 2))

	def test_tuple_deep_replace(self):
		d1 = {"a": ({"b": 1}, {"c": 2})}
		self.assertEqual({"a": ({"b": 1}, {"c": 20})}, deep_replace(d1, "a.1.c", 20))

	def test_dataclass_deep_replace(self):
		@dataclass(frozen=True)
		class A:
			a: int

		d1 = ({"a1": A(1)}, {"a2": A(2)})
		self.assertEqual(({"a1": A(1)}, {"a2": A(20)}), deep_replace(d1, "1.a2.a", 20))
