import sys

from PyQt5.QtCore import QSize, Qt
from PyQt5.QtWidgets import QApplication, QMainWindow
from dataclasses import asdict

from common_qt.message_handler import install_qt_message_handler
from slide_viewer.ui.dict_tree_view_model.action.context_menu_factory import context_menu_factory2
from slide_viewer.ui.odict.odict import ODictModel, ManualThresholdFilterODictModel
from slide_viewer.ui.odict.odicts_tree_model import ODictsTreeModelSelectMode
from deepable_qt.deepable_tree_view import DeepableTreeView
from img.filter.threshold_filter import ThresholdType
from img.filter.manual_threshold import ManualThresholdFilterData
from img.filter.base_filter import FilterType
from img.color_mode import ColorMode
from slide_viewer.filter.filter_odicts_tree_model import FilterODictsTreeModel

odicts = [
    ManualThresholdFilterODictModel({
        ODictModel.odict_display_attrs: ['id'],
        ODictModel.odict_decoration_attr: "color_prop",
        ODictModel.odict_checked_attr: "default_filter",
        "color_prop": "red",
        "default_filter": True,
        **asdict(ManualThresholdFilterData("1", FilterType.THRESHOLD, ThresholdType.MANUAL, ColorMode.L,
                                           (120, 180)))
    }),
    ManualThresholdFilterODictModel({
        ODictModel.odict_display_attrs: ['id'],
        ODictModel.odict_decoration_attr: "color_prop",
        ODictModel.odict_checked_attr: "default_filter",
        "color_prop": "red",
        "default_filter": True,
        **asdict(ManualThresholdFilterData("2", FilterType.THRESHOLD, ThresholdType.MANUAL, ColorMode.HSV,
                                           ((120, 0, 0), (180, 255, 255))))
    })
]
if __name__ == "__main__":
    install_qt_message_handler()
    app = QApplication(sys.argv)
    window = QMainWindow()
    model = FilterODictsTreeModel([], ODictsTreeModelSelectMode.odict_rows, radio_attr="default_filter")
    model.set_odicts(odicts)
    view = DeepableTreeView(model, window)
    view.setContextMenuPolicy(Qt.CustomContextMenu)
    view.customContextMenuRequested.connect(context_menu_factory2(view))

    window.setCentralWidget(view)

    window.show()
    window.resize(QSize(700, 700))

    sys.exit(app.exec_())
