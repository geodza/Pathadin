import unittest

from deepable.core import deep_get, deep_diff, DeepDiffChange, DeepDiffChanges


class DeepDiffTest(unittest.TestCase):

	def test_deep_diff(self):
		d1 = {
			"a": {
				"b": {
					"c": 1
				},
				"f": 0
			}
		}
		d2 = {
			"a": {
				"b": {
					"c": 2
				},
				"e": 3
			}
		}
		df = deep_diff(d1, d2)
		print(df)
		self.assertEqual(df, DeepDiffChanges({"a.f"}, {"a.e": 3}, {"a.b.c": DeepDiffChange(1, 2)}))
