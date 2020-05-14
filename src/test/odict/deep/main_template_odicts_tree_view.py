import copy
import sys

from PyQt5.QtCore import QSize, Qt
from PyQt5.QtWidgets import QApplication, QMainWindow, QDockWidget, QLabel

from common_qt.message_handler import install_qt_message_handler
from deepable_qt.context_menu_factory2 import context_menu_factory2
from deepable_qt.tree_view_config_deepable_tree_model import TreeViewConfigDeepableTreeModel
from deepable_qt.deepable_tree_view import DeepableTreeView
from src.test.odict._data import odict1

if __name__ == "__main__":
    install_qt_message_handler()
    app = QApplication(sys.argv)
    window = QMainWindow()

    model = TreeViewConfigDeepableTreeModel()
    model.set_root(odict1)
    view = DeepableTreeView(window)
    view.setModel(model)
    view.setContextMenuPolicy(Qt.CustomContextMenu)
    view.customContextMenuRequested.connect(context_menu_factory2(view))

    model2 = TreeViewConfigDeepableTreeModel()
    model2.set_root(copy.deepcopy(odict1))
    view2 = DeepableTreeView(window)
    view2.setModel(model2)
    view2.setContextMenuPolicy(Qt.CustomContextMenu)
    view2.customContextMenuRequested.connect(context_menu_factory2(view2))

    dw = QDockWidget('items1', window)
    dw.setWidget(view)
    dw.setFeatures(dw.features() & ~QDockWidget.DockWidgetClosable)
    window.addDockWidget(Qt.RightDockWidgetArea, dw)

    dw2 = QDockWidget('items2', window)
    dw2.setWidget(view2)
    dw2.setFeatures(dw2.features() & ~QDockWidget.DockWidgetClosable)
    window.addDockWidget(Qt.RightDockWidgetArea, dw2)

    label = QLabel('central widget')
    window.setCentralWidget(label)

    window.show()
    window.resize(QSize(700, 700))
    sys.exit(app.exec_())
