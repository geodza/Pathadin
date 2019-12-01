from abc import ABC, abstractmethod
from typing import Optional

from PyQt5.QtGui import QIcon

from slide_viewer.ui.slide.widget.icons import IconName


class IconProvider(ABC):

    @abstractmethod
    def get_icon(self, icon_name: IconName) -> Optional[QIcon]:
        pass
