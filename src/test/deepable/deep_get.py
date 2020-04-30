import unittest

from deepable.core import deep_get


class DeepGetTest(unittest.TestCase):

	def test_deep_get(self):
		d1 = {"a": {"b": {"c": 1}}}
		g1 = deep_get(d1, "a.b.c")
		self.assertEqual(1, g1)
