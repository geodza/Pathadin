import typing

from PyQt5.QtCore import Qt, QMargins
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QSplitter, QLabel, QGroupBox

from slide_viewer.ui.dict_tree_view_model.action.context_menu_factory import context_menu_factory
from slide_viewer.ui.dict_tree_view_model.ordered_dicts_tree_view import OrderedDictsTreeView
from slide_viewer.ui.dict_tree_view_model.standard_attr_key import StandardAttrKey


class OrderedDictsTreeWidget(QWidget):

    def __init__(self, parent: typing.Optional[QWidget] = None) -> None:
        super().__init__(parent)

        self.instances_view = OrderedDictsTreeView(self)
        self.instances_view.setContextMenuPolicy(Qt.CustomContextMenu)

        self.templates_view = OrderedDictsTreeView(self)
        self.templates_view.setContextMenuPolicy(Qt.CustomContextMenu)
        self.templates_view.modelChanged.connect(self.update_default_template)
        self.templates_view.odictsChanged.connect(self.on_odict_changed)
        self.templates_view.odictsInserted.connect(self.update_default_template)
        self.templates_view.odictsRemoved.connect(self.update_default_template)

        self.instances_view.customContextMenuRequested.connect(
            context_menu_factory(self.instances_view, self.templates_view, False))
        self.templates_view.customContextMenuRequested.connect(
            context_menu_factory(self.instances_view, self.templates_view, True))

        templates_group = QGroupBox("Annotation templates", self)
        templates_layout = QVBoxLayout(templates_group)
        # templates_layout.addWidget(QLabel("Annotation templates"))
        templates_layout.addWidget(self.templates_view)
        templates_group.setLayout(templates_layout)

        annotations_group = QGroupBox("Annotations", self)
        annotations_layout = QVBoxLayout(annotations_group)
        annotations_layout.addWidget(self.instances_view)
        annotations_group.setLayout(annotations_layout)

        layout = QVBoxLayout()
        self.splitter = QSplitter(Qt.Vertical)
        self.splitter.addWidget(templates_group)
        self.splitter.addWidget(annotations_group)
        layout.addWidget(self.splitter)
        self.splitter.setStretchFactor(0, 0)
        self.splitter.setStretchFactor(1, 1)

        layout.setContentsMargins(QMargins())
        self.setLayout(layout)

    def on_odict_changed(self, odict_numbers: typing.Iterable[int]):
        default_template_number = self.find_first_default_odict(odict_numbers)
        self.update_default_template(default_template_number)

    def find_first_default_odict(self, odict_numbers: typing.Iterable[int]):
        default_template_number = None
        for template_number in odict_numbers:
            odict = self.templates_view.model().get_odict(template_number)
            if odict.get(StandardAttrKey.default_template.name, False):
                default_template_number = template_number
                break
        return default_template_number

    def update_default_template(self, default_template_number=None):
        if default_template_number is None and self.templates_view.model().rowCount():
            default_template_number = self.find_first_default_odict(range(self.templates_view.model().rowCount()))
            if default_template_number is None:
                default_template_number = 0
        for template_number in range(self.templates_view.model().rowCount()):
            odict = self.templates_view.model().get_odict(template_number)
            attr_value = odict.get(StandardAttrKey.default_template.name, False)
            is_default = template_number == default_template_number
            if attr_value != is_default:
                self.templates_view.model().edit_attr_by_key(template_number, StandardAttrKey.default_template.name,
                                                             not attr_value)
