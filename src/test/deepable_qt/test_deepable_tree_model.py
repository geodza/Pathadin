import unittest

from deepable_qt.deepable_tree_model import DeepableTreeModel


class DeepableTreeModelTest(unittest.TestCase):

	def test1(self):
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
