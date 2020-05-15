import sys

from PyQt5 import QtCore
from PyQt5.QtCore import QSize
from PyQt5.QtWidgets import QApplication, QMainWindow

from common_qt.util.message_handler import qt_message_handler
from deepable_qt.deepable_tree_model import DeepableTreeModel
from deepable_qt.deepable_tree_model_delegate import DeepableTreeModelDelegate

from deepable_qt.deepable_tree_view import DeepableTreeView

if __name__ == "__main__":
	QtCore.qInstallMessageHandler(qt_message_handler)
	app = QApplication(sys.argv)
	window = QMainWindow()
	d1 = [{"a": 10}, {"b": 20}, {"c": 30}]
	model = DeepableTreeModel(_modelDelegate=DeepableTreeModelDelegate())
	model.root = d1
	view = DeepableTreeView(window)
	view.setModel(model)

	window.setCentralWidget(view)

	window.show()
	window.resize(QSize(700, 700))

	sys.exit(app.exec_())