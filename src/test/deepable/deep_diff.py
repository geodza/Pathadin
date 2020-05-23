import unittest

from deepable.core import deep_get, deep_diff_ignore_order, DeepDiffChange, DeepDiffChange as DDC, DeepDiffChanges


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
		df = deep_diff_ignore_order(d1, d2)
		print(df)
		self.assertEqual(df, DeepDiffChanges({"a.f"}, {"a.e": 3}, {"a.b.c": DDC(1, 2)}))

	def test_list_deep_diff(self):
		d1 = [{"a": 10}, {"b": 20}, {"c": 30}]
		d2 = [{"a": 10}, {"b": 22}, {"d": 40}]
		df = deep_diff_ignore_order(d1, d2)
		self.assertEqual(df, DeepDiffChanges(set(), {}, {"2":DDC({"c":30},{"d":40}) ,"1.b": DDC(20, 22)}))

	def test_dict_deep_diff2(self):
		d1 = [{"a": 10}, {"b": 20}, {"c": 30}, {"d": None}]
		d2 = [{"a": 10}, {"b": 22}, {"d": 40}, {"d": {"d1": 1}}]
		df = deep_diff_ignore_order(d1, d2)
		self.assertEqual(df, DeepDiffChanges(set(), {}, {"3.d":DeepDiffChange(None, {"d1":1}), "1.b": DeepDiffChange(20, 22), "2":DeepDiffChange({"c":30},{"d":40})}))

	def test_dict_deep_diff3(self):
		d1 = [{"a": 10}, {"b": 20}, {"c": 30}]
		d2 = [{"a": 10}, {"b": 22}, {"d": 40}, {"d": {"d1": 1}}]
		df = deep_diff_ignore_order(d1, d2)
		self.assertEqual(df, DeepDiffChanges(set(), {"3":{"d":{"d1": 1}}}, {"1.b": DeepDiffChange(20, 22), "2":DeepDiffChange({"c":30},{"d":40})}))
