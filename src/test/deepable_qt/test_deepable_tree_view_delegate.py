import sys
import typing

from PyQt5 import QtCore
from PyQt5.QtCore import QSize, QModelIndex, Qt
from PyQt5.QtWidgets import QApplication, QMainWindow, QStyledItemDelegate, QWidget, QStyleOptionViewItem

from common_qt.mvc.view.delegate.composite_item_view_delegate import CompositeItemViewDelegate
from common_qt.mvc.view.delegate.factory.abstract_item_view_delegate_factory import AbstractItemViewDelegateFactory, T
from common_qt.mvc.view.delegate.abstract_item_view_delegate import AbstractItemViewDelegate
from common_qt.mvc.view.delegate.styled_item_view_delegate import QStyledItemViewDelegate
from common_qt.util.message_handler import qt_message_handler
from deepable_qt.model.deepable_tree_model import DeepableTreeModel
from deepable_qt.model.standard_deepable_tree_model_delegate import StandardDeepableTreeModelDelegate

from deepable_qt.view.deepable_tree_view import DeepableTreeView

if __name__ == "__main__":
	QtCore.qInstallMessageHandler(qt_message_handler)
	app = QApplication(sys.argv)
	window = QMainWindow()
	d1 = {
		"a": {
			"b": {
				"c": "abc",
				"s": "def",
			},
			"f": "ghj",
		}
	}


	class D1Factory(AbstractItemViewDelegateFactory):
		class D1(AbstractItemViewDelegate):

			def setEditorData(self, editor: QWidget, index: QModelIndex) -> None:
				value = index.data(Qt.EditRole)
				d1_value = f"d1 - {value}"
				editor.metaObject().userProperty().write(editor, d1_value)
			# super().setEditorData(editor, index)

		def create(self, index: QModelIndex) -> typing.Optional[AbstractItemViewDelegate]:
			if index.column()==1:
				return D1Factory.D1()


	class D2Factory(AbstractItemViewDelegateFactory):
		class D2(AbstractItemViewDelegate):

			def setEditorData(self, editor: QWidget, index: QModelIndex) -> None:
				super().setEditorData(editor, index)

		def create(self, index: QModelIndex) -> typing.Optional[AbstractItemViewDelegate]:
			return D2Factory.D2()


	model = DeepableTreeModel(_modelDelegate=StandardDeepableTreeModelDelegate())
	model.root = d1
	view = DeepableTreeView(window)
	view.setModel(model)
	item_delegate = QStyledItemViewDelegate(
		CompositeItemViewDelegate([
			D1Factory(),
			D2Factory()
		]))
	view.setItemDelegate(item_delegate)

	window.setCentralWidget(view)

	window.show()
	window.resize(QSize(700, 700))

	sys.exit(app.exec_())
