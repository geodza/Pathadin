import unittest

from deepable_qt.deepable_tree_model import DeepableTreeModel


class DeepableTreeModelTest(unittest.TestCase):

	def test_dict_tree_model(self):
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
		model = DeepableTreeModel()
		model.root = d1
		model["a"] = d2["a"]
		self.assertEqual(model.root, d2)

	def test_list_tree_model(self):
		d1 = [{"a": 10}, {"b": 20}, {"c": 30}]
		d2 = [{"a": 10}, {"b": 22}, {"d": 40}]
		model = DeepableTreeModel()
		model.root = d1
		model["1"] = d2[1]
		model["2"] = d2[2]
		self.assertEqual(model.root, d2)
