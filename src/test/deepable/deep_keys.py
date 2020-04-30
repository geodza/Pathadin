import unittest

from deepable.core import deep_get, deep_keys_deep


class DeepKeysTest(unittest.TestCase):

	def test_deep_keys(self):
		d1 = {"a": {"b": {"c": 1, "d": 2}}, "f": 1}
		keys = deep_keys_deep(d1)
		print(keys)
