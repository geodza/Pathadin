from typing import Optional

from PyQt5.QtWidgets import QMenuBar, QWidget
from dataclasses import dataclass, InitVar

from common_qt.core import QMenuP
from slide_viewer.ui.slide.action.annotation_action_group import \
	AnnotationActionGroup
from slide_viewer.ui.slide.action.simple_actions import SimpleActions
from slide_viewer.ui.slide.action.zoom_action_group import ZoomActionGroup
from slide_viewer.ui.slide.widget.menu.grid_menu import GridMenu
from slide_viewer.ui.slide.widget.menu.sub_windows_menu import SubWindowsMenu
from slide_viewer.ui.slide.widget.menu.sync_menu import SyncMenu
from slide_viewer.ui.slide.widget.menu.view_menu import ViewMenu
from slide_viewer.ui.slide.widget.menu.zoom_menu import ZoomMenu


@dataclass
class Menubar(QMenuBar):
	parent_: InitVar[Optional[QWidget]]
	simple_actions: InitVar[SimpleActions]
	annotation_action_group: InitVar[AnnotationActionGroup]
	zoom_action_group: InitVar[ZoomActionGroup]
	sync_menu: InitVar[SyncMenu]

	def __post_init__(self, parent_: Optional[QWidget], simple_actions: SimpleActions,
					  annotation_action_group: AnnotationActionGroup, zoom_action_group: ZoomActionGroup,
					  sync_menu: SyncMenu):
		super().__init__(parent_)
		self.addMenu(SubWindowsMenu(parent_, simple_actions, sync_menu))
		self.addMenu(ViewMenu(parent_, simple_actions))
		self.addMenu(ZoomMenu(parent_, simple_actions, zoom_action_group))
		self.addMenu(GridMenu(parent_, simple_actions))
		self.addMenu(QMenuP('Annotations', parent_, annotation_action_group.actions()))
