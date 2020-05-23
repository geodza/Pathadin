import sys
import typing

from PyQt5 import QtCore
from PyQt5.QtCore import QSize
from PyQt5.QtWidgets import QApplication, QMainWindow

from common_qt.mvc.model.delegate.item_model_delegate import AbstractItemModelDelegate
from common_qt.mvc.model.delegate.composite_item_model_delegate import CompositeAbstractItemModelDelegate
from common_qt.mvc.model.delegate.factory.item_model_delegate_factory import AbstractItemModelDelegateFactory, T
from common_qt.util.message_handler import qt_message_handler
from deepable_qt.model.standard_deepable_tree_model_delegate import StandardDeepableTreeModelDelegate

from deepable_qt.view.deepable_tree_view import DeepableTreeView
from deepable_qt.model.deepable_tree_model import DeepableTreeModel

if __name__ == "__main__":
	QtCore.qInstallMessageHandler(qt_message_handler)
	app = QApplication(sys.argv)
	window = QMainWindow()
	d1 = {
		"a": {
			"b": {
				"c": 1,
				"s": "0",
			},
			"f": 0,
		}
	}


	class A(AbstractItemModelDelegateFactory):

		def create(self, index: T) -> typing.Optional[AbstractItemModelDelegate[T]]:
			return StandardDeepableTreeModelDelegate()


	# model = DeepableTreeModel(_modelDelegate=DeepableTreeModelDelegate())
	model = DeepableTreeModel(_modelDelegate=CompositeAbstractItemModelDelegate([A()]))
	model.root = d1
	view = DeepableTreeView(window)
	view.setModel(model)

	window.setCentralWidget(view)

	window.show()
	window.resize(QSize(700, 700))

	sys.exit(app.exec_())
