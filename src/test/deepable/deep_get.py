import unittest

from deepable.core import deep_get


class DeepGetTest(unittest.TestCase):

	def test_dict_deep_get(self):
		d1 = {"a": {"b": {"c": 1}}}
		g1 = deep_get(d1, "a.b.c")
		self.assertEqual(1, g1)

	def test_list_deep_get(self):
		d1 = [{"a": 10}, {"b": 20}]
		self.assertEqual({"b": 20}, deep_get(d1, "1"))
		self.assertEqual(20, deep_get(d1, "1.b"))
