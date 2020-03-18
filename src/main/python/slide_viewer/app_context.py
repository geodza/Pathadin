from typing import Optional

from PyQt5.QtCore import Qt
from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import QToolBar
from fbs_runtime.application_context.PyQt5 import ApplicationContext

from common.debug_only_decorator import debug_only
from common_qt.abcq_meta import ABCQMeta
from slide_viewer.config import slide_path
from slide_viewer.ui.slide.action.annotation_action_group import AnnotationActionGroup
from slide_viewer.ui.slide.action.simple_actions import SimpleActions
from slide_viewer.ui.slide.action.sync_action_group import SyncActionGroup
from slide_viewer.ui.slide.action.zoom_action_group import ZoomActionGroup
from slide_viewer.ui.slide.action.zoom_editor import ZoomEditor
from common_qt.dynamic_command_widget import DynamicCommandWidget
from slide_viewer.ui.slide.widget.icons import IconName
from slide_viewer.ui.slide.widget.interface.icon_provider import IconProvider
from slide_viewer.ui.slide.widget.main_window import MainWindow
from slide_viewer.ui.slide.widget.menu.sync_menu import SyncMenu
from slide_viewer.ui.slide.widget.menubar import Menubar
from slide_viewer.ui.slide.widget.toolbar import Toolbar


class AppContext(ApplicationContext, IconProvider, metaclass=ABCQMeta):

    def get_icon(self, icon_name: IconName) -> Optional[QIcon]:
        if not icon_name:
            return None
        icon_svg_name = f'{icon_name.name}.svg'
        return QIcon(self.get_resource(icon_svg_name))

    def __init__(self):
        super().__init__()
        mw = MainWindow()

        simple_actions = SimpleActions(parent_=mw, active_view_provider=mw, active_annotation_tree_view_provider=mw,
                                       sub_window_service=mw,
                                       icon_provider=self)
        zoom_action_group = ZoomActionGroup(parent_=mw, active_view_provider=mw, sub_window_service=mw)
        zoom_editor = ZoomEditor(parent_=mw, active_view_provider=mw, sub_window_service=mw)

        annotation_action_group = AnnotationActionGroup(parent_=mw, active_view_provider=mw, sub_window_service=mw,
                                                        icon_provider=self)
        sync_action_group = SyncActionGroup(parent_=mw, active_view_provider=mw, sub_window_service=mw,
                                            icon_provider=self)
        sync_menu = SyncMenu(parent_=mw, sync_action_group=sync_action_group)
        toolbar = Toolbar(parent_=mw, simple_actions=simple_actions,
                          zoom_action_group=zoom_action_group,
                          annotation_action_group=annotation_action_group, zoom_editor=zoom_editor,
                          sync_menu=sync_menu)
        menubar = Menubar(parent_=mw, simple_actions=simple_actions, annotation_action_group=annotation_action_group,
                          zoom_action_group=zoom_action_group, sync_menu=sync_menu)

        mw.addToolBar(toolbar)
        mw.setMenuBar(menubar)
        self.main_window = mw
        self.add_debug_toolbar()

    @debug_only()
    def add_debug_toolbar(self):
        mw = self.main_window
        dynamic_command_toolbar = QToolBar("Dynamic command. self.ref references to main window", mw)
        dynamic_command = DynamicCommandWidget(mw)
        dynamic_command_toolbar.addWidget(dynamic_command)
        mw.addToolBar(Qt.BottomToolBarArea, dynamic_command_toolbar)

    def run(self):
        self.main_window.show()
        windows = 1
        widgets = []
        # w = self.main_window.add_sub_window()
        # w.show()
        for i in range(windows):
            w = self.main_window.add_sub_window()
            w.widget().id = i
            # w.widget().graphics_view_annotation_service.annotation_pixmap_provider.id = i
            if slide_path:
                w.widget().set_file_path(slide_path)
            # w.widget().annotation_service.add(
            #     AnnotationModel(geometry=AnnotationGeometry(annotation_type=AnnotationType.ELLIPSE, origin_point=(0, 0), points=[(0, 0), (300, 300)]),
            #                     id="", label="", filter_id="1"))
            # w.widget().annotation_service.add(
            #     AnnotationModel(geometry=AnnotationGeometry(annotation_type=AnnotationType.POLYGON, origin_point=(500, 500),
            #                                                 points=[(0, 0), (300, 300), (0, 300), (0, 0)]),
            #                     id="", label="", filter_id="2"))
            # w.widget().annotation_service.add(
            #     AnnotationModel(geometry=AnnotationGeometry(annotation_type=AnnotationType.RECT, origin_point=(41472, 63232),
            #                                                 points=[(0, 0), (255, 255)]),
            #                     id="", label="", filter_id="1",filter_level=0))
            w.show()
            # load_annotations(w1.widget(), slide_annotations_path)
            widgets.append(w)
        self.main_window.tile_sub_windows()
        for w in widgets:
            w.widget().fit_scene()
        return self.app.exec_()
